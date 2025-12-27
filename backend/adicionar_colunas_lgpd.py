import sys
sys.path.insert(0, '.')
from dotenv import load_dotenv
load_dotenv()
from sqlalchemy import create_engine, text
import os

print("🔄 Adicionando colunas LGPD ao PostgreSQL...")

engine = create_engine(os.getenv('DATABASE_URL'))

comandos = [
    "ALTER TABLE pacientes_regulacao ADD COLUMN IF NOT EXISTS nome_completo VARCHAR",
    "ALTER TABLE pacientes_regulacao ADD COLUMN IF NOT EXISTS nome_mae VARCHAR",
    "ALTER TABLE pacientes_regulacao ADD COLUMN IF NOT EXISTS cpf VARCHAR",
    "ALTER TABLE pacientes_regulacao ADD COLUMN IF NOT EXISTS telefone_contato VARCHAR",
    "ALTER TABLE pacientes_regulacao ADD COLUMN IF NOT EXISTS data_nascimento TIMESTAMP",
    "ALTER TABLE pacientes_regulacao ADD COLUMN IF NOT EXISTS cid VARCHAR",
    "ALTER TABLE pacientes_regulacao ADD COLUMN IF NOT EXISTS cid_desc VARCHAR",
    "ALTER TABLE pacientes_regulacao ADD COLUMN IF NOT EXISTS historico_paciente TEXT",
    "ALTER TABLE pacientes_regulacao ADD COLUMN IF NOT EXISTS prioridade_descricao VARCHAR",
    "CREATE INDEX IF NOT EXISTS idx_pacientes_cpf ON pacientes_regulacao(cpf)",
]

with engine.connect() as conn:
    for i, cmd in enumerate(comandos, 1):
        try:
            print(f"  [{i}/{len(comandos)}] Executando...")
            conn.execute(text(cmd))
            conn.commit()
            print(f"  ✅ OK")
        except Exception as e:
            print(f"  ⚠️ {e}")

print("\n✅ Colunas adicionadas!")
print("\n📋 Verificando...")

with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'pacientes_regulacao'
        AND column_name IN ('nome_completo', 'nome_mae', 'cpf', 'telefone_contato', 'cid', 'historico_paciente')
        ORDER BY column_name
    """))
    colunas = result.fetchall()
    if colunas:
        print("✅ Colunas LGPD criadas:")
        for col in colunas:
            print(f"  - {col[0]}")
    else:
        print("❌ Nenhuma coluna encontrada")
