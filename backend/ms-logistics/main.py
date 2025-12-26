from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt
import logging
import sys
import os
from typing import Optional, List

# Adicionar o diretório pai ao path para importar shared
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared.database import get_db, PacienteRegulacao, Usuario, create_tables

app = FastAPI(title="MS-Logistics", description="Microserviço de Logística e Autenticação")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurações JWT
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "sua_chave_secreta_jwt_muito_segura_aqui")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # 8 horas

# Configurações de senha
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Modelos Pydantic
class UserCreate(BaseModel):
    email: EmailStr
    nome: str
    senha: str
    tipo_usuario: str  # REGULADOR, HOSPITAL, ADMIN
    unidade_vinculada: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    senha: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user_info: dict

class TransferenciaRequest(BaseModel):
    protocolo: str
    unidade_destino: str
    tipo_transporte: str
    observacoes: Optional[str] = None

class StatusUpdate(BaseModel):
    protocolo: str
    novo_status: str
    observacoes: Optional[str] = None

# Funções de autenticação
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(Usuario).filter(Usuario.email == email).first()
    if user is None:
        raise credentials_exception
    
    return user

def require_role(allowed_roles: List[str]):
    def role_checker(current_user: Usuario = Depends(get_current_user)):
        if current_user.tipo_usuario not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker

@app.on_event("startup")
async def startup_event():
    """Inicialização do serviço"""
    create_tables()
    
    # Criar usuário admin padrão se não existir
    db = next(get_db())
    admin_user = db.query(Usuario).filter(Usuario.email == "admin@sesgo.gov.br").first()
    if not admin_user:
        admin_user = Usuario(
            email="admin@sesgo.gov.br",
            nome="Administrador SES-GO",
            senha_hash=get_password_hash("admin123"),
            tipo_usuario="ADMIN"
        )
        db.add(admin_user)
        db.commit()
        logger.info("Usuário admin criado: admin@sesgo.gov.br / admin123")
    
    logger.info("MS-Logistics iniciado com sucesso")

@app.get("/")
async def root():
    return {"service": "MS-Logistics", "status": "running", "version": "1.0.0"}

@app.post("/register", response_model=dict)
async def register_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["ADMIN"]))
):
    """Registrar novo usuário (apenas admins)"""
    
    # Verificar se email já existe
    existing_user = db.query(Usuario).filter(Usuario.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email já cadastrado"
        )
    
    # Criar usuário
    db_user = Usuario(
        email=user.email,
        nome=user.nome,
        senha_hash=get_password_hash(user.senha),
        tipo_usuario=user.tipo_usuario,
        unidade_vinculada=user.unidade_vinculada
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return {"message": "Usuário criado com sucesso", "user_id": db_user.id}

@app.post("/login", response_model=Token)
async def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Login de usuário"""
    
    user = db.query(Usuario).filter(Usuario.email == user_credentials.email).first()
    
    if not user or not verify_password(user_credentials.senha, user.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.ativo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário inativo"
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_info": {
            "id": user.id,
            "email": user.email,
            "nome": user.nome,
            "tipo_usuario": user.tipo_usuario,
            "unidade_vinculada": user.unidade_vinculada
        }
    }

@app.get("/me")
async def get_current_user_info(current_user: Usuario = Depends(get_current_user)):
    """Informações do usuário atual"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "nome": current_user.nome,
        "tipo_usuario": current_user.tipo_usuario,
        "unidade_vinculada": current_user.unidade_vinculada
    }

@app.post("/transferencia")
async def autorizar_transferencia(
    transferencia: TransferenciaRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["REGULADOR", "ADMIN"]))
):
    """Autorizar transferência de paciente"""
    
    # Buscar paciente
    paciente = db.query(PacienteRegulacao).filter(
        PacienteRegulacao.protocolo == transferencia.protocolo
    ).first()
    
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    
    if paciente.status != "EM_REGULACAO":
        raise HTTPException(
            status_code=400, 
            detail=f"Paciente não está em regulação. Status atual: {paciente.status}"
        )
    
    # Atualizar status
    paciente.status = "INTERNACAO_AUTORIZADA"
    paciente.unidade_destino = transferencia.unidade_destino
    paciente.updated_at = datetime.utcnow()
    
    db.commit()
    
    logger.info(f"Transferência autorizada por {current_user.email}: {transferencia.protocolo} -> {transferencia.unidade_destino}")
    
    return {
        "message": "Transferência autorizada com sucesso",
        "protocolo": transferencia.protocolo,
        "unidade_destino": transferencia.unidade_destino,
        "autorizado_por": current_user.nome
    }

@app.post("/atualizar-status")
async def atualizar_status_paciente(
    status_update: StatusUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["REGULADOR", "HOSPITAL", "ADMIN"]))
):
    """Atualizar status do paciente"""
    
    # Buscar paciente
    paciente = db.query(PacienteRegulacao).filter(
        PacienteRegulacao.protocolo == status_update.protocolo
    ).first()
    
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    
    # Validar transições de status
    status_validos = ["EM_REGULACAO", "INTERNACAO_AUTORIZADA", "INTERNADA", "COM_ALTA"]
    if status_update.novo_status not in status_validos:
        raise HTTPException(status_code=400, detail="Status inválido")
    
    # Verificar permissões por tipo de usuário
    if current_user.tipo_usuario == "HOSPITAL":
        # Hospitais só podem confirmar internação ou alta
        if status_update.novo_status not in ["INTERNADA", "COM_ALTA"]:
            raise HTTPException(
                status_code=403, 
                detail="Hospital só pode confirmar internação ou alta"
            )
    
    status_anterior = paciente.status
    paciente.status = status_update.novo_status
    paciente.updated_at = datetime.utcnow()
    
    db.commit()
    
    logger.info(f"Status atualizado por {current_user.email}: {status_update.protocolo} {status_anterior} -> {status_update.novo_status}")
    
    return {
        "message": "Status atualizado com sucesso",
        "protocolo": status_update.protocolo,
        "status_anterior": status_anterior,
        "novo_status": status_update.novo_status,
        "atualizado_por": current_user.nome
    }

@app.get("/fila-regulacao")
async def get_fila_regulacao(
    especialidade: Optional[str] = None,
    cidade: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["REGULADOR", "ADMIN"]))
):
    """Buscar fila de regulação"""
    
    query = db.query(PacienteRegulacao).filter(
        PacienteRegulacao.status == "EM_REGULACAO"
    )
    
    if especialidade:
        query = query.filter(PacienteRegulacao.especialidade.ilike(f"%{especialidade}%"))
    
    if cidade:
        query = query.filter(PacienteRegulacao.cidade_origem.ilike(f"%{cidade}%"))
    
    # Ordenar por prioridade e data
    pacientes = query.order_by(
        PacienteRegulacao.score_prioridade.desc().nullslast(),
        PacienteRegulacao.data_solicitacao.asc()
    ).all()
    
    return [
        {
            "protocolo": p.protocolo,
            "data_solicitacao": p.data_solicitacao.isoformat() if p.data_solicitacao else None,
            "especialidade": p.especialidade,
            "cidade_origem": p.cidade_origem,
            "unidade_solicitante": p.unidade_solicitante,
            "score_prioridade": p.score_prioridade,
            "classificacao_risco": p.classificacao_risco,
            "justificativa_tecnica": p.justificativa_tecnica
        } for p in pacientes
    ]

@app.get("/dashboard-regulador")
async def dashboard_regulador(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["REGULADOR", "ADMIN"]))
):
    """Dashboard para reguladores"""
    
    # Estatísticas gerais
    total_em_regulacao = db.query(PacienteRegulacao).filter(
        PacienteRegulacao.status == "EM_REGULACAO"
    ).count()
    
    total_autorizadas = db.query(PacienteRegulacao).filter(
        PacienteRegulacao.status == "INTERNACAO_AUTORIZADA"
    ).count()
    
    total_internadas = db.query(PacienteRegulacao).filter(
        PacienteRegulacao.status == "INTERNADA"
    ).count()
    
    # Pacientes críticos (score > 7)
    criticos = db.query(PacienteRegulacao).filter(
        PacienteRegulacao.status == "EM_REGULACAO",
        PacienteRegulacao.score_prioridade > 7
    ).count()
    
    # Tempo médio de regulação (últimas 24h)
    ontem = datetime.utcnow() - timedelta(days=1)
    regulacoes_recentes = db.query(PacienteRegulacao).filter(
        PacienteRegulacao.data_solicitacao >= ontem,
        PacienteRegulacao.status.in_(["INTERNACAO_AUTORIZADA", "INTERNADA"])
    ).all()
    
    tempo_medio = 0
    if regulacoes_recentes:
        tempos = []
        for p in regulacoes_recentes:
            if p.updated_at and p.data_solicitacao:
                tempo_regulacao = (p.updated_at - p.data_solicitacao).total_seconds() / 3600
                tempos.append(tempo_regulacao)
        
        if tempos:
            tempo_medio = sum(tempos) / len(tempos)
    
    return {
        "estatisticas": {
            "em_regulacao": total_em_regulacao,
            "autorizadas": total_autorizadas,
            "internadas": total_internadas,
            "criticos": criticos,
            "tempo_medio_regulacao_h": round(tempo_medio, 2)
        },
        "usuario": {
            "nome": current_user.nome,
            "tipo": current_user.tipo_usuario
        },
        "ultima_atualizacao": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)