"""
Script para adicionar coluna hospital_origem na tabela pacientes_regulacao
Permite calcular distancia entre hospital de origem e destino
"""

import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Carregar .env do diretorio backend
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./regulacao.db")
print(f"Usando banco de dados: {DATABASE_URL[:50]}...")

def adicionar_coluna_hospital_origem():
    """Adiciona coluna hospital_origem se nao existir"""
    
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # Verificar se coluna ja existe
        if 'sqlite' in DATABASE_URL:
            result = conn.execute(text("PRAGMA table_info(pacientes_regulacao)"))
            colunas = [row[1] for row in result.fetchall()]
        else:
            # PostgreSQL
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'pacientes_regulacao'
            """))
            colunas = [row[0] for row in result.fetchall()]
        
        print(f"Colunas encontradas: {len(colunas)}")
        
        if 'hospital_origem' not in colunas:
            print("Adicionando coluna hospital_origem...")
            
            try:
                if 'sqlite' in DATABASE_URL:
                    conn.execute(text("""
                        ALTER TABLE pacientes_regulacao 
                        ADD COLUMN hospital_origem VARCHAR(255)
                    """))
                else:
                    # PostgreSQL
                    conn.execute(text("""
                        ALTER TABLE pacientes_regulacao 
                        ADD COLUMN hospital_origem VARCHAR(255) NULL
                    """))
                
                conn.commit()
                print("Coluna hospital_origem adicionada com sucesso!")
            except Exception as e:
                print(f"Erro ao adicionar coluna: {e}")
        else:
            print("Coluna hospital_origem ja existe.")
        
        # Verificar colunas atuais
        if 'sqlite' in DATABASE_URL:
            result = conn.execute(text("PRAGMA table_info(pacientes_regulacao)"))
            colunas = [row[1] for row in result.fetchall()]
        else:
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'pacientes_regulacao'
                ORDER BY ordinal_position
            """))
            colunas = [row[0] for row in result.fetchall()]
        
        print(f"\nColunas atuais da tabela pacientes_regulacao ({len(colunas)}):")
        for col in colunas:
            print(f"  - {col}")

if __name__ == "__main__":
    adicionar_coluna_hospital_origem()
