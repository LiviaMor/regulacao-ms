#!/usr/bin/env python3
"""
Sistema de Regulação SES-GO - Versão Simplificada
Funciona sem Docker, PostgreSQL ou dependências complexas
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from datetime import datetime, timedelta
import json
import time
import jwt
from passlib.context import CryptContext

# Configurações
SECRET_KEY = "demo_secret_key_change_in_production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480

# Configurações de senha
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Criar aplicação FastAPI
app = FastAPI(
    title="Sistema de Regulação Autônoma SES-GO",
    description="API Simplificada para Demonstração",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos Pydantic
class UserLogin(BaseModel):
    email: str
    senha: str

class PacienteInput(BaseModel):
    protocolo: str
    especialidade: str = "CLINICA MÉDICA"
    cid: str = "Z00.0"
    cid_desc: str = "Exame médico geral"
    prontuario_texto: str = ""
    historico_paciente: str = ""
    prioridade_descricao: str = "Normal"

class TransferenciaRequest(BaseModel):
    protocolo: str
    unidade_destino: str
    tipo_transporte: str
    observacoes: str = ""

# Dados simulados
DADOS_DASHBOARD = {
    "status_summary": [
        {"status": "EM_REGULACAO", "count": 25},
        {"status": "INTERNACAO_AUTORIZADA", "count": 8},
        {"status": "INTERNADA", "count": 156},
        {"status": "COM_ALTA", "count": 43}
    ],
    "unidades_pressao": [
        {
            "unidade_executante_desc": "HOSPITAL ESTADUAL DR ALBERTO RASSI HGG",
            "cidade": "GOIANIA",
            "pacientes_em_fila": 12
        },
        {
            "unidade_executante_desc": "HOSPITAL DE URGENCIAS DE GOIAS",
            "cidade": "GOIANIA", 
            "pacientes_em_fila": 8
        },
        {
            "unidade_executante_desc": "HOSPITAL ESTADUAL DE FORMOSA",
            "cidade": "FORMOSA",
            "pacientes_em_fila": 5
        }
    ]
}

FILA_REGULACAO = [
    {
        "protocolo": f"REG-{i:04d}",
        "data_solicitacao": datetime.utcnow().isoformat(),
        "especialidade": ["CARDIOLOGIA", "ORTOPEDIA", "NEUROLOGIA", "CLINICA MÉDICA"][i % 4],
        "cidade_origem": ["GOIANIA", "ANAPOLIS", "FORMOSA", "CATALAO"][i % 4],
        "unidade_solicitante": f"Hospital Municipal {i}",
        "score_prioridade": (i % 10) + 1,
        "classificacao_risco": ["VERDE", "AMARELO", "VERMELHO"][i % 3],
        "justificativa_tecnica": f"Paciente necessita avaliação especializada em {['CARDIOLOGIA', 'ORTOPEDIA', 'NEUROLOGIA', 'CLINICA MÉDICA'][i % 4]}"
    }
    for i in range(1, 11)
]

# Funções auxiliares
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        return {"email": email}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

def simular_processamento_ia(paciente: PacienteInput) -> dict:
    """Simula processamento com IA baseado nos dados do paciente"""
    
    # Determinar risco baseado no CID e prioridade
    risco = "VERDE"
    score = 3
    
    if paciente.cid.startswith("I21") or "infarto" in paciente.prontuario_texto.lower():
        risco = "VERMELHO"
        score = 9
    elif paciente.cid.startswith("I") or "emergencia" in paciente.prioridade_descricao.lower():
        risco = "AMARELO" 
        score = 7
    elif "urgente" in paciente.prioridade_descricao.lower():
        risco = "AMARELO"
        score = 6
    
    # Selecionar unidade baseada na especialidade
    unidades_por_especialidade = {
        "CARDIOLOGIA": "HOSPITAL ESTADUAL DR ALBERTO RASSI HGG",
        "ORTOPEDIA": "HOSPITAL DE URGENCIAS DE GOIAS",
        "NEUROLOGIA": "HOSPITAL ESTADUAL DR ALBERTO RASSI HGG",
        "CLINICA MÉDICA": "HOSPITAL ESTADUAL DE FORMOSA"
    }
    
    unidade_destino = unidades_por_especialidade.get(
        paciente.especialidade, 
        "HOSPITAL ESTADUAL DR ALBERTO RASSI HGG"
    )
    
    return {
        "analise_decisoria": {
            "score_prioridade": score,
            "classificacao_risco": risco,
            "unidade_destino_sugerida": unidade_destino,
            "justificativa_clinica": f"Paciente com {paciente.especialidade} - {paciente.cid_desc}. Score calculado baseado em protocolos clínicos e análise de risco."
        },
        "logistica": {
            "acionar_ambulancia": risco in ["VERMELHO", "AMARELO"],
            "tipo_transporte": "USA" if risco == "VERMELHO" else "USB",
            "previsao_vaga_h": "1-2 horas" if risco == "VERMELHO" else "2-4 horas"
        },
        "protocolo_especial": {
            "tipo": "UTI" if risco == "VERMELHO" else "NORMAL",
            "instrucoes_imediatas": "Monitorização contínua e suporte avançado" if risco == "VERMELHO" else "Cuidados padrão de transporte"
        },
        "metadata": {
            "tempo_processamento": 1.2,
            "biobert_usado": False,
            "llama_usado": False,
            "timestamp": datetime.utcnow().isoformat(),
            "modo": "simulacao"
        }
    }

# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    return {
        "service": "Sistema de Regulação Autônoma SES-GO",
        "status": "running",
        "version": "2.0.0-simplified",
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints": {
            "dashboard": "/dashboard/leitos",
            "auth": "/login",
            "ai": "/processar-regulacao",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "mode": "simplified",
        "dependencies": {
            "database": "sqlite_memory",
            "ai_engine": "simulation",
            "biobert": False,
            "llama": False
        }
    }

@app.get("/dashboard/leitos")
async def get_dashboard_leitos():
    """Dashboard público de leitos"""
    return {
        **DADOS_DASHBOARD,
        "ultima_atualizacao": datetime.utcnow().isoformat()
    }

@app.post("/login")
async def login(user_credentials: UserLogin):
    """Login de usuário"""
    
    # Credenciais de demonstração
    if user_credentials.email == "admin@sesgo.gov.br" and user_credentials.senha == "admin123":
        access_token = create_access_token(data={"sub": user_credentials.email})
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_info": {
                "id": 1,
                "email": user_credentials.email,
                "nome": "Administrador Demo SES-GO",
                "tipo_usuario": "ADMIN",
                "unidade_vinculada": "SES-GO"
            }
        }
    
    raise HTTPException(
        status_code=401,
        detail="Email ou senha incorretos"
    )

@app.post("/processar-regulacao")
async def processar_regulacao_ia(paciente: PacienteInput):
    """Processamento com IA simulada"""
    
    if not paciente.protocolo:
        raise HTTPException(status_code=400, detail="Protocolo obrigatório")
    
    # Simular tempo de processamento
    time.sleep(1)
    
    resultado = simular_processamento_ia(paciente)
    
    return resultado

@app.get("/fila-regulacao")
async def get_fila_regulacao(current_user: dict = Depends(verify_token)):
    """Buscar fila de regulação (requer autenticação)"""
    return FILA_REGULACAO

@app.post("/transferencia")
async def autorizar_transferencia(
    transferencia: TransferenciaRequest,
    current_user: dict = Depends(verify_token)
):
    """Autorizar transferência de paciente (requer autenticação)"""
    
    return {
        "message": "Transferência autorizada com sucesso",
        "protocolo": transferencia.protocolo,
        "unidade_destino": transferencia.unidade_destino,
        "tipo_transporte": transferencia.tipo_transporte,
        "autorizado_por": current_user["email"],
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/dashboard-regulador")
async def dashboard_regulador(current_user: dict = Depends(verify_token)):
    """Dashboard para reguladores (requer autenticação)"""
    
    return {
        "estatisticas": {
            "em_regulacao": 25,
            "autorizadas": 8,
            "internadas": 156,
            "criticos": 3,
            "tempo_medio_regulacao_h": 1.8
        },
        "usuario": {
            "email": current_user["email"],
            "nome": "Administrador Demo SES-GO",
            "tipo": "ADMIN"
        },
        "ultima_atualizacao": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    print("🏥 Iniciando Sistema de Regulação SES-GO (Versão Simplificada)")
    print("📡 Servidor: http://localhost:8000")
    print("📚 Documentação: http://localhost:8000/docs")
    print("🔐 Login demo: admin@sesgo.gov.br / admin123")
    uvicorn.run(app, host="0.0.0.0", port=8000)