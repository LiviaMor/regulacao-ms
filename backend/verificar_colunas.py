#!/usr/bin/env python3
"""
Script para verificar colunas da tabela pacientes_regulacao
Funciona com SQLite e PostgreSQL
"""

import sys
sys.path.insert(0, '.')
from dotenv import load_dotenv
load_dotenv()
from sqlalchemy import create_engine, text, inspect
import os

# Obter DATABASE_URL do .env
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./regulacao.db')

print(f"🔍 Conectando ao banco de dados...")
print(f"📍 URL: {DATABASE_URL.split('@')[0]}...")  # Não mostrar senha

try:
    engine = create_engine(DATABASE_URL)
    
    # Detectar tipo de banco
    dialect_name = engine.dialect.name
    print(f"💾 Tipo de banco: {dialect_name.upper()}")
    
    with engine.connect() as conn:
        # Usar query apropriada para cada banco
        if dialect_name == 'postgresql':
            # PostgreSQL usa information_schema
            result = conn.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'pacientes_regulacao'
                ORDER BY ordinal_position
            """))
            
            print('\n✅ Colunas na tabela pacientes_regulacao (PostgreSQL):')
            print(f"{'Coluna':<40} {'Tipo':<20}")
            print("=" * 60)
            
            count = 0
            for row in result:
                print(f"{row[0]:<40} {row[1]:<20}")
                count += 1
            
            print("=" * 60)
            print(f"📊 Total: {count} colunas")
            
        elif dialect_name == 'sqlite':
            # SQLite usa PRAGMA
            result = conn.execute(text("PRAGMA table_info(pacientes_regulacao)"))
            
            print('\n✅ Colunas na tabela pacientes_regulacao (SQLite):')
            print(f"{'Coluna':<40} {'Tipo':<20}")
            print("=" * 60)
            
            count = 0
            for row in result:
                # row = (cid, name, type, notnull, dflt_value, pk)
                print(f"{row[1]:<40} {row[2]:<20}")
                count += 1
            
            print("=" * 60)
            print(f"📊 Total: {count} colunas")
            
        else:
            # Fallback: usar inspector do SQLAlchemy
            inspector = inspect(engine)
            columns = inspector.get_columns('pacientes_regulacao')
            
            print(f'\n✅ Colunas na tabela pacientes_regulacao ({dialect_name}):')
            print(f"{'Coluna':<40} {'Tipo':<20}")
            print("=" * 60)
            
            for col in columns:
                print(f"{col['name']:<40} {str(col['type']):<20}")
            
            print("=" * 60)
            print(f"📊 Total: {len(columns)} colunas")
        
        # Verificar colunas específicas importantes
        print("\n🔍 Verificando colunas críticas:")
        
        colunas_criticas = [
            'protocolo',
            'status',
            'nome_completo',
            'cpf',
            'especialidade',
            'cid',
            'tipo_transporte',
            'status_ambulancia',
            'data_solicitacao_ambulancia'
        ]
        
        if dialect_name == 'sqlite':
            result = conn.execute(text("PRAGMA table_info(pacientes_regulacao)"))
            colunas_existentes = [row[1] for row in result]
        else:
            inspector = inspect(engine)
            colunas_existentes = [col['name'] for col in inspector.get_columns('pacientes_regulacao')]
        
        for coluna in colunas_criticas:
            if coluna in colunas_existentes:
                print(f"  ✅ {coluna}")
            else:
                print(f"  ❌ {coluna} - FALTANDO!")
        
        print("\n✅ Verificação concluída com sucesso!")
        
except Exception as e:
    print(f"\n❌ Erro ao conectar ao banco de dados:")
    print(f"   {str(e)}")
    print(f"\n💡 Dicas:")
    print(f"   1. Verifique se o PostgreSQL está rodando")
    print(f"   2. Verifique o arquivo .env")
    print(f"   3. Verifique se o banco 'regulacao_db' existe")
    print(f"   4. Verifique usuário e senha")
    sys.exit(1)

