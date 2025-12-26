from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./regulacao.db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelos de Dados Compartilhados
class PacienteRegulacao(Base):
    __tablename__ = "pacientes_regulacao"
    
    id = Column(Integer, primary_key=True, index=True)
    protocolo = Column(String, unique=True, index=True)
    data_solicitacao = Column(DateTime)
    status = Column(String)  # EM_REGULACAO, INTERNACAO_AUTORIZADA, INTERNADA, COM_ALTA
    tipo_leito = Column(String)
    especialidade = Column(String)
    cpf_mascarado = Column(String)
    codigo_procedimento = Column(String)
    unidade_solicitante = Column(String)
    cidade_origem = Column(String)
    unidade_destino = Column(String, nullable=True)
    data_atualizacao = Column(DateTime)
    complexo_regulador = Column(String)
    
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