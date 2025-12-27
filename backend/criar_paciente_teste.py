import sys
sys.path.insert(0, '.')
from dotenv import load_dotenv
load_dotenv()
from shared.database import SessionLocal, PacienteRegulacao
from datetime import datetime

db = SessionLocal()

# Criar paciente de teste
paciente_teste = PacienteRegulacao(
    protocolo="REG-2025-TEST-001",
    nome_completo="João da Silva Santos",
    nome_mae="Maria da Silva",
    cpf="12345678901",
    telefone_contato="62987654321",
    data_solicitacao=datetime.utcnow(),
    status="EM_REGULACAO",
    especialidade="CARDIOLOGIA",
    cid="I21.0",
    cid_desc="Infarto agudo do miocárdio",
    cidade_origem="GOIANIA",
    unidade_solicitante="Hospital Teste",
    classificacao_risco="VERMELHO",
    score_prioridade=9
)

db.add(paciente_teste)
db.commit()

print("✅ Paciente de teste criado!")
print(f"   Protocolo: {paciente_teste.protocolo}")
print(f"   Nome: {paciente_teste.nome_completo}")
print(f"   CPF: {paciente_teste.cpf}")
print(f"   Telefone: {paciente_teste.telefone_contato}")

db.close()
