from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

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
    status = Column(String)  # AGUARDANDO_REGULACAO, EM_REGULACAO, EM_TRANSFERENCIA, EM_TRANSITO, ADMITIDO, ALTA, NEGADO_PENDENTE
    tipo_leito = Column(String)
    especialidade = Column(String)
    cpf_mascarado = Column(String)
    codigo_procedimento = Column(String)
    unidade_solicitante = Column(String)
    cidade_origem = Column(String)
    unidade_destino = Column(String, nullable=True)
    data_atualizacao = Column(DateTime)
    complexo_regulador = Column(String)
    
    # ============================================================================
    # DADOS PESSOAIS DO PACIENTE (LGPD - Art. 5º, I e II)
    # Campos obrigatórios para identificação e contato
    # ============================================================================
    nome_completo = Column(String, nullable=True)  # Nome completo do paciente
    nome_mae = Column(String, nullable=True)  # Nome da mãe (identificação secundária)
    cpf = Column(String, nullable=True, index=True)  # CPF completo (criptografado em produção)
    telefone_contato = Column(String, nullable=True)  # Telefone para contato
    data_nascimento = Column(DateTime, nullable=True)  # Data de nascimento
    
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
    
    # ============================================================================
    # CAMPOS DE TRANSFERÊNCIA E AMBULÂNCIA
    # ============================================================================
    tipo_transporte = Column(String, nullable=True)  # 'USA', 'USB', 'AEROMÉDICO'
    status_ambulancia = Column(String, nullable=True)  # 'SOLICITADA', 'A_CAMINHO', 'NO_LOCAL', 'TRANSPORTANDO', 'CONCLUIDA'
    data_solicitacao_ambulancia = Column(DateTime, nullable=True)
    data_internacao = Column(DateTime, nullable=True)
    observacoes_transferencia = Column(Text, nullable=True)
    
    # Dados obrigatórios de transferência (conforme especificação)
    identificacao_ambulancia = Column(String, nullable=True)  # Placa/ID da ambulância
    distancia_km = Column(Float, nullable=True)  # Distância entre unidades
    tempo_estimado_min = Column(Integer, nullable=True)  # Tempo estimado de transporte
    
    # ============================================================================
    # CAMPOS DE AUDITORIA E ALTA
    # ============================================================================
    data_entrega_destino = Column(DateTime, nullable=True)  # Quando paciente foi entregue
    data_alta = Column(DateTime, nullable=True)  # Data/hora da alta hospitalar
    observacoes_alta = Column(Text, nullable=True)  # Observações da alta
    justificativa_negacao = Column(Text, nullable=True)  # Motivo da negação (se negado)
    
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
    microservico_origem = Column(String, nullable=True)  # MS-Hospital, MS-Regulacao, MS-Transferencia
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

# ============================================================================
# FUNÇÕES DE ANONIMIZAÇÃO (LGPD - Art. 12)
# Para consultas públicas e dashboards sem autenticação
# ============================================================================

def anonimizar_nome(nome_completo: str) -> str:
    """
    Anonimiza nome completo mantendo apenas primeira letra de cada nome
    Exemplo: "João da Silva Santos" -> "J*** d* S*** S***"
    """
    if not nome_completo:
        return "***"
    
    partes = nome_completo.strip().split()
    anonimizado = []
    
    for parte in partes:
        if len(parte) <= 2:
            # Preposições (de, da, do, dos, das) mantém
            anonimizado.append(parte.lower())
        else:
            # Primeira letra + asteriscos
            anonimizado.append(parte[0].upper() + "*" * (len(parte) - 1))
    
    return " ".join(anonimizado)

def anonimizar_cpf(cpf: str) -> str:
    """
    Anonimiza CPF mantendo apenas últimos 2 dígitos
    Exemplo: "123.456.789-01" -> "***.***.*89-01"
    """
    if not cpf:
        return "***.***.***-**"
    
    # Remove formatação
    cpf_limpo = ''.join(filter(str.isdigit, cpf))
    
    if len(cpf_limpo) != 11:
        return "***.***.***-**"
    
    # Mantém apenas últimos 2 dígitos
    return f"***.***.*{cpf_limpo[7:9]}-{cpf_limpo[9:11]}"

def anonimizar_telefone(telefone: str) -> str:
    """
    Anonimiza telefone mantendo apenas DDD e últimos 2 dígitos
    Exemplo: "(62) 98765-4321" -> "(62) ****-**21"
    """
    if not telefone:
        return "(**) ****-****"
    
    # Remove formatação
    tel_limpo = ''.join(filter(str.isdigit, telefone))
    
    if len(tel_limpo) < 10:
        return "(**) ****-****"
    
    ddd = tel_limpo[:2]
    ultimos = tel_limpo[-2:]
    
    if len(tel_limpo) == 11:  # Celular
        return f"({ddd}) *****-**{ultimos}"
    else:  # Fixo
        return f"({ddd}) ****-**{ultimos}"

def anonimizar_paciente(paciente: PacienteRegulacao) -> dict:
    """
    Retorna dados do paciente anonimizados para consultas públicas
    Mantém apenas informações não sensíveis e dados anonimizados
    """
    return {
        "protocolo": paciente.protocolo,
        "nome_anonimizado": anonimizar_nome(paciente.nome_completo) if paciente.nome_completo else "***",
        "cpf_anonimizado": anonimizar_cpf(paciente.cpf) if paciente.cpf else "***.***.***-**",
        "telefone_anonimizado": anonimizar_telefone(paciente.telefone_contato) if paciente.telefone_contato else "(**) ****-****",
        "data_solicitacao": paciente.data_solicitacao.isoformat() if paciente.data_solicitacao else None,
        "status": paciente.status,
        "especialidade": paciente.especialidade,
        "cidade_origem": paciente.cidade_origem,
        "unidade_solicitante": paciente.unidade_solicitante,
        "unidade_destino": paciente.unidade_destino,
        "classificacao_risco": paciente.classificacao_risco,
        "data_atualizacao": paciente.data_atualizacao.isoformat() if paciente.data_atualizacao else None,
        # Informações de transferência e ambulância
        "status_ambulancia": getattr(paciente, 'status_ambulancia', None),
        "tipo_transporte": getattr(paciente, 'tipo_transporte', None),
        "data_solicitacao_ambulancia": getattr(paciente, 'data_solicitacao_ambulancia', None).isoformat() if getattr(paciente, 'data_solicitacao_ambulancia', None) else None,
    }

def paciente_completo(paciente: PacienteRegulacao) -> dict:
    """
    Retorna dados completos do paciente (apenas para usuários autenticados)
    ATENÇÃO: Usar apenas em endpoints protegidos com autenticação
    """
    return {
        "protocolo": paciente.protocolo,
        "nome_completo": paciente.nome_completo,
        "nome_mae": paciente.nome_mae,
        "cpf": paciente.cpf,
        "telefone_contato": paciente.telefone_contato,
        "data_nascimento": paciente.data_nascimento.isoformat() if paciente.data_nascimento else None,
        "data_solicitacao": paciente.data_solicitacao.isoformat() if paciente.data_solicitacao else None,
        "status": paciente.status,
        "tipo_leito": paciente.tipo_leito,
        "especialidade": paciente.especialidade,
        "cid": paciente.cid,
        "cid_desc": paciente.cid_desc,
        "cidade_origem": paciente.cidade_origem,
        "unidade_solicitante": paciente.unidade_solicitante,
        "unidade_destino": paciente.unidade_destino,
        "classificacao_risco": paciente.classificacao_risco,
        "score_prioridade": paciente.score_prioridade,
        "justificativa_tecnica": paciente.justificativa_tecnica,
        "historico_paciente": paciente.historico_paciente,
        "data_atualizacao": paciente.data_atualizacao.isoformat() if paciente.data_atualizacao else None,
    }