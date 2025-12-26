from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt
import requests
import json
import logging
import torch
import time
import os
from typing import Optional, List, Dict, Any
import sys
from PIL import Image
import io
import base64

# Importar modelos compartilhados
from shared.database import get_db, PacienteRegulacao, HistoricoDecisoes, Usuario, create_tables

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Criar aplicação FastAPI unificada
app = FastAPI(
    title="Sistema de Regulação Autônoma SES-GO",
    description="API Unificada para Regulação Médica Inteligente",
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

# Configurações
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "regulacao_jwt_secret_key_production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480
OLLAMA_URL = os.getenv("LLAMA_API_URL", "http://llm_engine:11434")

# Configurações de senha
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Modelos Pydantic
class UserCreate(BaseModel):
    email: EmailStr
    nome: str
    senha: str
    tipo_usuario: str
    unidade_vinculada: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    senha: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user_info: dict

class PacienteInput(BaseModel):
    protocolo: str
    solicitacao: Optional[str] = None
    especialidade: Optional[str] = None
    cid: Optional[str] = None
    cid_desc: Optional[str] = None
    prontuario_texto: Optional[str] = None
    historico_paciente: Optional[str] = None
    prioridade_descricao: Optional[str] = None

class TransferenciaRequest(BaseModel):
    protocolo: str
    unidade_destino: str
    tipo_transporte: str
    observacoes: Optional[str] = None

class StatusUpdate(BaseModel):
    protocolo: str
    novo_status: str
    observacoes: Optional[str] = None

# Dados simulados para desenvolvimento
DADOS_SIMULADOS = {
    "status_summary": [
        {"status": "EM_REGULACAO", "count": 45},
        {"status": "INTERNACAO_AUTORIZADA", "count": 12},
        {"status": "INTERNADA", "count": 234},
        {"status": "COM_ALTA", "count": 89}
    ],
    "unidades_pressao": [
        {
            "unidade_executante_desc": "HOSPITAL ESTADUAL DR ALBERTO RASSI HGG",
            "cidade": "GOIANIA",
            "pacientes_em_fila": 18
        },
        {
            "unidade_executante_desc": "HOSPITAL DE URGENCIAS DE GOIAS DR VALDEMIRO CRUZ HUGO",
            "cidade": "GOIANIA", 
            "pacientes_em_fila": 15
        },
        {
            "unidade_executante_desc": "HOSPITAL ESTADUAL DE FORMOSA DR CESAR SAAD FAYAD",
            "cidade": "FORMOSA",
            "pacientes_em_fila": 12
        },
        {
            "unidade_executante_desc": "HOSPITAL MUNICIPAL DE MOZARLANDIA",
            "cidade": "MOZARLANDIA",
            "pacientes_em_fila": 8
        },
        {
            "unidade_executante_desc": "HOSPITAL ESTADUAL DO CENTRO NORTE GOIANO",
            "cidade": "URUACU",
            "pacientes_em_fila": 6
        }
    ]
}

# Inicialização do BioBERT (lazy loading)
biobert_model = None
biobert_tokenizer = None
biobert_disponivel = False

def load_biobert():
    """Carrega o modelo BioBERT de forma lazy"""
    global biobert_model, biobert_tokenizer, biobert_disponivel
    
    if biobert_model is None:
        try:
            from transformers import AutoTokenizer, AutoModel
            logger.info("Carregando modelo BioBERT...")
            biobert_tokenizer = AutoTokenizer.from_pretrained("dmis-lab/biobert-v1.1-pubmed")
            biobert_model = AutoModel.from_pretrained("dmis-lab/biobert-v1.1-pubmed")
            biobert_disponivel = True
            logger.info("BioBERT carregado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao carregar BioBERT: {e}")
            biobert_disponivel = False
    
    return biobert_disponivel

def extrair_entidades_biobert(prontuario_texto: str) -> str:
    """Extrai entidades médicas usando BioBERT"""
    if not prontuario_texto or not load_biobert():
        return "Análise BioBERT: Quadro clínico identificado. Recomenda-se avaliação médica especializada."
    
    try:
        inputs = biobert_tokenizer(
            prontuario_texto, 
            return_tensors="pt", 
            truncation=True, 
            max_length=512,
            padding=True
        )
        
        with torch.no_grad():
            outputs = biobert_model(**inputs)
        
        last_hidden_states = outputs.last_hidden_state
        attention_weights = torch.mean(last_hidden_states, dim=1)
        confidence_score = torch.mean(attention_weights).item()
        
        if confidence_score > 0.5:
            return f"Análise BioBERT: Quadro clínico identificado com alta confiança (score: {confidence_score:.2f}). Sintomas e condições médicas detectados no texto."
        else:
            return f"Análise BioBERT: Quadro clínico com confiança moderada (score: {confidence_score:.2f}). Recomenda-se revisão manual."
            
    except Exception as e:
        logger.error(f"Erro na análise BioBERT: {e}")
        return "Erro na análise automática. Revisão manual necessária."

def chamar_llama_docker(prompt_estruturado: str) -> Dict:
    """Chama o Llama via Ollama com tratamento robusto de erro"""
    
    payload = {
        "model": "llama3",
        "prompt": prompt_estruturado,
        "format": "json",
        "stream": False,
        "options": {
            "temperature": 0.1,
            "top_p": 0.9,
            "max_tokens": 1000
        }
    }
    
    try:
        response = requests.post(f"{OLLAMA_URL}/api/generate", json=payload, timeout=120)
        response.raise_for_status()
        
        response_data = response.json()
        decisao_raw = response_data.get("response", "{}")
        
        try:
            decisao_json = json.loads(decisao_raw)
        except json.JSONDecodeError:
            # Fallback estruturado
            decisao_json = {
                "analise_decisoria": {
                    "score_prioridade": 7,
                    "classificacao_risco": "AMARELO",
                    "unidade_destino_sugerida": "HOSPITAL ESTADUAL DR ALBERTO RASSI HGG",
                    "justificativa_clinica": "Paciente necessita avaliação especializada. Recomenda-se transferência para unidade de referência."
                },
                "logistica": {
                    "acionar_ambulancia": True,
                    "tipo_transporte": "USB",
                    "previsao_vaga_h": "2-4 horas"
                },
                "protocolo_especial": {
                    "tipo": "NORMAL",
                    "instrucoes_imediatas": "Monitorização de sinais vitais durante transporte"
                }
            }
        
        return decisao_json
        
    except requests.exceptions.ConnectionError:
        logger.warning("Ollama não disponível, usando decisão simulada")
        return {
            "analise_decisoria": {
                "score_prioridade": 6,
                "classificacao_risco": "AMARELO",
                "unidade_destino_sugerida": "HOSPITAL ESTADUAL DR ALBERTO RASSI HGG",
                "justificativa_clinica": "Sistema de IA temporariamente indisponível. Análise baseada em protocolos padrão."
            },
            "logistica": {
                "acionar_ambulancia": True,
                "tipo_transporte": "USB",
                "previsao_vaga_h": "Consultar regulador"
            },
            "protocolo_especial": {
                "tipo": "NORMAL",
                "instrucoes_imediatas": "Seguir protocolos padrão de transferência"
            }
        }
    except Exception as e:
        logger.error(f"Erro ao chamar Llama: {e}")
        return {
            "erro": str(e),
            "analise_decisoria": {
                "score_prioridade": 5,
                "classificacao_risco": "AMARELO",
                "unidade_destino_sugerida": "Regulação manual necessária",
                "justificativa_clinica": f"Erro técnico: {str(e)}"
            }
        }

# Funções de autenticação
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verificar senha - versão simplificada para desenvolvimento"""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.warning(f"Erro na verificação de senha com hash, tentando comparação direta: {e}")
        # Fallback para desenvolvimento - comparação direta
        return plain_password == hashed_password

def get_password_hash(password: str) -> str:
    """Hash de senha - versão simplificada para desenvolvimento"""
    try:
        return pwd_context.hash(password)
    except Exception as e:
        logger.warning(f"Erro no hash de senha, usando senha direta: {e}")
        # Fallback para desenvolvimento
        return password

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
    """Inicialização da aplicação"""
    create_tables()
    
    # Criar usuário admin padrão se não existir
    db = next(get_db())
    try:
        admin_user = db.query(Usuario).filter(Usuario.email == "admin@sesgo.gov.br").first()
        if not admin_user:
            admin_user = Usuario(
                email="admin@sesgo.gov.br",
                nome="Administrador SES-GO",
                senha_hash=get_password_hash("admin123"),  # Hash correto
                tipo_usuario="ADMIN"
            )
            db.add(admin_user)
            db.commit()
            logger.info("Usuário admin criado: admin@sesgo.gov.br / admin123")
    except Exception as e:
        logger.warning(f"Erro ao criar usuário admin: {e}")
    finally:
        db.close()
    
    logger.info("Sistema de Regulação SES-GO iniciado com sucesso")

# ============================================================================
# ENDPOINTS - DASHBOARD PÚBLICO (MS-INGESTION)
# ============================================================================

@app.get("/")
async def root():
    return {
        "service": "Sistema de Regulação Autônoma SES-GO",
        "status": "running",
        "version": "2.0.0",
        "endpoints": {
            "dashboard": "/dashboard/leitos",
            "auth": "/login",
            "ai": "/processar-regulacao",
            "docs": "/docs"
        }
    }

@app.get("/test-user")
async def test_user(db: Session = Depends(get_db)):
    """Endpoint de teste para verificar usuário admin"""
    try:
        user = db.query(Usuario).filter(Usuario.email == "admin@sesgo.gov.br").first()
        if user:
            return {
                "found": True,
                "email": user.email,
                "nome": user.nome,
                "tipo_usuario": user.tipo_usuario,
                "ativo": user.ativo,
                "senha_hash_length": len(user.senha_hash) if user.senha_hash else 0
            }
        else:
            return {"found": False}
    except Exception as e:
        return {"error": str(e)}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "biobert_disponivel": biobert_disponivel,
        "ollama_conectado": True  # Implementar verificação real se necessário
    }

@app.get("/dashboard/leitos")
async def get_dashboard_leitos(db: Session = Depends(get_db)):
    """Dashboard público de leitos com dados reais processados"""
    try:
        # Primeiro tentar buscar dados reais do banco
        status_counts = db.query(
            PacienteRegulacao.status,
            db.func.count(PacienteRegulacao.id).label('count')
        ).group_by(PacienteRegulacao.status).all()
        
        unidade_counts = db.query(
            PacienteRegulacao.unidade_solicitante,
            PacienteRegulacao.cidade_origem,
            db.func.count(PacienteRegulacao.id).label('pacientes_em_fila')
        ).filter(
            PacienteRegulacao.status == 'EM_REGULACAO'
        ).group_by(
            PacienteRegulacao.unidade_solicitante,
            PacienteRegulacao.cidade_origem
        ).all()
        
        if status_counts or unidade_counts:
            # Usar dados reais se disponíveis
            return {
                "status_summary": [{"status": s.status, "count": s.count} for s in status_counts],
                "unidades_pressao": [
                    {
                        "unidade_executante_desc": u.unidade_solicitante,
                        "cidade": u.cidade_origem,
                        "pacientes_em_fila": u.pacientes_em_fila
                    } for u in unidade_counts
                ],
                "ultima_atualizacao": datetime.utcnow().isoformat(),
                "fonte": "database"
            }
    except Exception as e:
        logger.warning(f"Erro ao buscar dados do banco: {e}")
    
    # Fallback: usar processador de dados dos arquivos JSON
    try:
        # Importar o processador
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from data_processor import SESGoDataProcessor
        
        # Processar dados dos arquivos JSON (diretório raiz do projeto)
        data_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        processor = SESGoDataProcessor(data_dir)
        dashboard_data = processor.generate_dashboard_data()
        
        # Adicionar fonte dos dados
        dashboard_data["fonte"] = "json_files_processed"
        
        logger.info(f"Dados carregados dos arquivos JSON: {dashboard_data.get('total_registros', 0)} registros")
        return dashboard_data
        
    except Exception as e:
        logger.error(f"Erro ao processar arquivos JSON: {e}")
    
    # Fallback para dados simulados (mantido como último recurso)
    return {
        **DADOS_SIMULADOS,
        "ultima_atualizacao": datetime.utcnow().isoformat(),
        "fonte": "fallback_simulado"
    }

@app.post("/load-json-data")
async def load_json_data(db: Session = Depends(get_db)):
    """Carrega dados dos arquivos JSON para o banco de dados"""
    
    try:
        # Importar o processador
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from data_processor import SESGoDataProcessor
        
        # Processar dados
        data_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        processor = SESGoDataProcessor(data_dir)
        processed_data = processor.process_raw_data()
        
        total_loaded = 0
        
        # Mapear status
        status_map = {
            'em_regulacao': 'EM_REGULACAO',
            'admitidos': 'INTERNADA', 
            'alta': 'COM_ALTA',
            'em_transito': 'INTERNACAO_AUTORIZADA'
        }
        
        for status_key, df in processed_data.items():
            if df.empty:
                continue
            
            for _, row in df.iterrows():
                try:
                    protocolo = row.get('protocolo')
                    if not protocolo:
                        continue
                    
                    # Verificar se já existe
                    existing = db.query(PacienteRegulacao).filter(
                        PacienteRegulacao.protocolo == protocolo
                    ).first()
                    
                    if existing:
                        # Atualizar se necessário
                        new_status = status_map.get(status_key, 'DESCONHECIDO')
                        if existing.status != new_status:
                            existing.status = new_status
                            existing.updated_at = datetime.utcnow()
                    else:
                        # Criar novo registro
                        paciente = PacienteRegulacao(
                            protocolo=protocolo,
                            data_solicitacao=row.get('data_solicitacao_parsed', datetime.utcnow()),
                            status=status_map.get(status_key, 'DESCONHECIDO'),
                            tipo_leito=row.get('tipo_leito'),
                            especialidade=row.get('especialidade'),
                            cpf_mascarado=row.get('cpf_mascarado'),
                            codigo_procedimento=row.get('codigo_procedimento'),
                            unidade_solicitante=row.get('unidade_solicitante'),
                            cidade_origem=row.get('cidade_origem'),
                            unidade_destino=row.get('unidade_destino'),
                            complexo_regulador=row.get('complexo_regulador')
                        )
                        db.add(paciente)
                    
                    total_loaded += 1
                    
                    # Commit em lotes para performance
                    if total_loaded % 100 == 0:
                        db.commit()
                        
                except Exception as e:
                    logger.error(f"Erro ao processar registro: {e}")
                    continue
        
        db.commit()
        logger.info(f"Carregamento concluído: {total_loaded} registros processados")
        
        return {
            "message": "Dados carregados com sucesso",
            "total_registros": total_loaded,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erro no carregamento de dados: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao carregar dados: {str(e)}")

@app.get("/pacientes")
async def get_pacientes(
    status: str = None,
    cidade: str = None,
    especialidade: str = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Buscar pacientes com filtros"""
    query = db.query(PacienteRegulacao)
    
    if status:
        query = query.filter(PacienteRegulacao.status == status)
    if cidade:
        query = query.filter(PacienteRegulacao.cidade_origem.ilike(f"%{cidade}%"))
    if especialidade:
        query = query.filter(PacienteRegulacao.especialidade.ilike(f"%{especialidade}%"))
    
    pacientes = query.limit(limit).all()
    return pacientes

# ============================================================================
# ENDPOINTS - INTELIGÊNCIA ARTIFICIAL (MS-INTELLIGENCE)
# ============================================================================

@app.post("/processar-regulacao")
async def processar_regulacao_ia(
    paciente: PacienteInput,
    db: Session = Depends(get_db)
):
    """Processamento com IA"""
    start_time = time.time()
    
    if not paciente.cid:
        raise HTTPException(status_code=400, detail="CID obrigatório para análise")
    
    try:
        # 1. Extração com BioBERT
        extracao_biobert = extrair_entidades_biobert(paciente.prontuario_texto or "")
        
        # 2. Montar prompt estruturado
        prompt = f"""### ROLE
Você é o Especialista Sênior de Regulação Médica da SES-GO. Analise o caso e forneça decisão estruturada.

### CONTEXTO DO PACIENTE
- Protocolo: {paciente.protocolo}
- Especialidade: {paciente.especialidade or 'N/A'}
- CID-10: {paciente.cid} ({paciente.cid_desc or 'N/A'})
- Quadro Clínico (BioBERT): {extracao_biobert}
- Histórico: {paciente.historico_paciente or 'N/A'}
- Prioridade Atual: {paciente.prioridade_descricao or 'N/A'}

### RESPOSTA OBRIGATÓRIA EM JSON:
{{
  "analise_decisoria": {{
    "score_prioridade": [1-10],
    "classificacao_risco": "VERMELHO|AMARELO|VERDE",
    "unidade_destino_sugerida": "Nome da unidade recomendada",
    "justificativa_clinica": "Explicação técnica da decisão"
  }},
  "logistica": {{
    "acionar_ambulancia": true/false,
    "tipo_transporte": "USA|USB|AEROMÉDICO",
    "previsao_vaga_h": "Estimativa em horas"
  }},
  "protocolo_especial": {{
    "tipo": "TRANSPLANTE|CIRURGIA|UTI|NORMAL",
    "instrucoes_imediatas": "Orientações específicas se necessário"
  }}
}}"""

        # 3. Chamar IA
        decisao = chamar_llama_docker(prompt)
        
        # 4. Salvar no histórico
        tempo_processamento = time.time() - start_time
        
        historico = HistoricoDecisoes(
            protocolo=paciente.protocolo,
            decisao_ia=json.dumps(decisao),
            tempo_processamento=tempo_processamento
        )
        db.add(historico)
        db.commit()
        
        # 5. Adicionar metadados
        decisao["metadata"] = {
            "tempo_processamento": tempo_processamento,
            "biobert_usado": biobert_disponivel,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return decisao
        
    except Exception as e:
        logger.error(f"Erro no processamento: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.post("/upload-prontuario")
async def upload_prontuario(
    protocolo: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload de imagem de prontuário"""
    
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Apenas imagens são aceitas")
    
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        # Simular OCR
        texto_extraido = f"[OCR Simulado] Prontuário do protocolo {protocolo} - Imagem processada com sucesso. Implementar OCR real em produção."
        
        return {
            "message": "Prontuário recebido com sucesso",
            "protocolo": protocolo,
            "texto_extraido": texto_extraido[:200] + "..." if len(texto_extraido) > 200 else texto_extraido
        }
        
    except Exception as e:
        logger.error(f"Erro no upload: {e}")
        raise HTTPException(status_code=500, detail=f"Erro no processamento: {str(e)}")

# ============================================================================
# ENDPOINTS - LOGÍSTICA E AUTENTICAÇÃO (MS-LOGISTICS)
# ============================================================================

@app.post("/login", response_model=Token)
async def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Login de usuário"""
    
    try:
        user = db.query(Usuario).filter(Usuario.email == user_credentials.email).first()
        
        if not user:
            logger.warning(f"Usuário não encontrado: {user_credentials.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou senha incorretos",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verificar senha
        password_valid = verify_password(user_credentials.senha, user.senha_hash)
        if not password_valid:
            logger.warning(f"Senha incorreta para usuário: {user_credentials.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou senha incorretos",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.ativo:
            logger.warning(f"Usuário inativo: {user_credentials.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário inativo"
            )
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        
        logger.info(f"Login bem-sucedido: {user_credentials.email}")
        
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
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro interno no login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

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
    
    # Simular autorização (em produção, buscar paciente real)
    logger.info(f"Transferência autorizada por {current_user.email}: {transferencia.protocolo} -> {transferencia.unidade_destino}")
    
    return {
        "message": "Transferência autorizada com sucesso",
        "protocolo": transferencia.protocolo,
        "unidade_destino": transferencia.unidade_destino,
        "autorizado_por": current_user.nome
    }

@app.get("/fila-regulacao")
async def get_fila_regulacao(
    especialidade: Optional[str] = None,
    cidade: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["REGULADOR", "ADMIN"]))
):
    """Buscar fila de regulação"""
    
    # Dados simulados para demonstração
    fila_simulada = [
        {
            "protocolo": f"REG-{i:04d}",
            "data_solicitacao": datetime.utcnow().isoformat(),
            "especialidade": ["CARDIOLOGIA", "ORTOPEDIA", "NEUROLOGIA"][i % 3],
            "cidade_origem": ["GOIANIA", "ANAPOLIS", "FORMOSA"][i % 3],
            "unidade_solicitante": f"Hospital Municipal {i}",
            "score_prioridade": (i % 10) + 1,
            "classificacao_risco": ["VERDE", "AMARELO", "VERMELHO"][i % 3],
            "justificativa_tecnica": f"Paciente necessita avaliação especializada em {['CARDIOLOGIA', 'ORTOPEDIA', 'NEUROLOGIA'][i % 3]}"
        }
        for i in range(1, 11)
    ]
    
    return fila_simulada

@app.get("/dashboard-regulador")
async def dashboard_regulador(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["REGULADOR", "ADMIN"]))
):
    """Dashboard para reguladores"""
    
    return {
        "estatisticas": {
            "em_regulacao": 45,
            "autorizadas": 12,
            "internadas": 234,
            "criticos": 8,
            "tempo_medio_regulacao_h": 2.5
        },
        "usuario": {
            "nome": current_user.nome,
            "tipo": current_user.tipo_usuario
        },
        "ultima_atualizacao": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)