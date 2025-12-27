"""
Modelos de dados compartilhados entre microserviços
Mantém compatibilidade com o sistema atual
"""

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente do .env (subir 2 níveis para encontrar backend/.env)
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    # Tentar carregar do diretório atual
    load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./regulacao.db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelos de Dados Compartilhados (mantidos do sistema atual)
class PacienteRegulacao(Base):
    __tablename__ = "pacientes_regulacao"
    
    id = Column(Integer, primary_key=True, index=True)
    protocolo = Column(String, unique=True, index=True)
    data_solicitacao = Column(DateTime)
    status = Column(String)  # EM_REGULACAO, INTERNACAO_AUTORIZADA, INTERNADA, COM_ALTA, REGULACAO_NEGADA, AGUARDANDO_REGULACAO
    tipo_leito = Column(String)
    especialidade = Column(String)
    cpf_mascarado = Column(String)
    codigo_procedimento = Column(String)
    unidade_solicitante = Column(String)
    cidade_origem = Column(String)
    unidade_destino = Column(String, nullable=True)
    data_atualizacao = Column(DateTime)
    complexo_regulador = Column(String)
    
    # Campos adicionais para área hospitalar
    cid = Column(String, nullable=True)
    cid_desc = Column(String, nullable=True)
    historico_paciente = Column(Text, nullable=True)
    prioridade_descricao = Column(String, nullable=True)
    
    # Campos para IA
    prontuario_texto = Column(Text, nullable=True)
    score_prioridade = Column(Integer, nullable=True)
    classificacao_risco = Column(String, nullable=True)
    justificativa_tecnica = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class HistoricoDecisoes(Base):
    __tablename__ = "historico_decisoes"
    
    id = Column(Integer, primary_key=True, index=True)
    protocolo = Column(String, index=True)
    decisao_ia = Column(Text)  # JSON da decisão da IA
    usuario_validador = Column(String, nullable=True)
    decisao_final = Column(Text, nullable=True)
    tempo_processamento = Column(Float)
    microservico_origem = Column(String, nullable=True)  # Novo campo para rastreabilidade
    created_at = Column(DateTime, default=datetime.utcnow)

class Usuario(Base):
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    nome = Column(String)
    senha_hash = Column(String)
    tipo_usuario = Column(String)  # REGULADOR, HOSPITAL, ADMIN
    unidade_vinculada = Column(String, nullable=True)
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# Novos modelos para microserviços futuros
class TransferenciaAmbulancia(Base):
    __tablename__ = "transferencias_ambulancia"
    
    id = Column(Integer, primary_key=True, index=True)
    protocolo = Column(String, index=True)
    tipo_transporte = Column(String)  # USA, USB, PROPRIO
    status_transferencia = Column(String)  # SOLICITADA, EM_TRANSITO, CONCLUIDA, CANCELADA
    unidade_origem = Column(String)
    unidade_destino = Column(String)
    data_solicitacao = Column(DateTime, default=datetime.utcnow)
    data_inicio_transporte = Column(DateTime, nullable=True)
    data_chegada = Column(DateTime, nullable=True)
    observacoes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class MedicacaoAltaComplexidade(Base):
    __tablename__ = "medicacao_alta_complexidade"
    
    id = Column(Integer, primary_key=True, index=True)
    protocolo = Column(String, index=True)
    medicamento = Column(String)
    dosagem = Column(String)
    frequencia = Column(String)
    duracao_tratamento = Column(String)
    status_dispensacao = Column(String)  # SOLICITADA, APROVADA, DISPENSADA, NEGADA
    justificativa_medica = Column(Text)
    unidade_solicitante = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Modelo para Memória de Curto Prazo - Histórico de Ocupação (MS-Ingestao)
class HistoricoOcupacao(Base):
    """
    Armazena histórico de ocupação para cálculo de tendências
    Usado pelo MS-Ingestao como "Memória de Curto Prazo" do sistema
    """
    __tablename__ = "historico_ocupacao"
    
    id = Column(Integer, primary_key=True, index=True)
    unidade_id = Column(String, index=True)  # ID/Sigla do hospital
    unidade_nome = Column(String)  # Nome completo do hospital
    tipo_leito = Column(String, index=True)  # UTI, ENFERMARIA, GERAL, etc.
    ocupacao_percentual = Column(Float)  # Taxa de ocupação (0-100)
    leitos_totais = Column(Integer)
    leitos_ocupados = Column(Integer)
    leitos_disponiveis = Column(Integer)
    data_coleta = Column(DateTime, default=datetime.utcnow, index=True)
    fonte_dados = Column(String, default="SCRAPER")  # SCRAPER, MANUAL, API, SIMULADOR


# Dependency para obter sessão do banco
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Criar todas as tabelas
def create_tables():
    Base.metadata.create_all(bind=engine)