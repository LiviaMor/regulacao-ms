#!/usr/bin/env python3
"""
Script para migrar banco de dados completo
Adiciona todas as colunas necessárias (LGPD + Transferência)
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

print("🚀 Iniciando migração completa do banco de dados...")
print(f"📍 URL: {DATABASE_URL.split('@')[0] if '@' in DATABASE_URL else DATABASE_URL}")

try:
    engine = create_engine(DATABASE_URL)
    dialect_name = engine.dialect.name
    
    print(f"💾 Tipo de banco: {dialect_name.upper()}")
    
    # Colunas a adicionar
    colunas_lgpd = [
        ("nome_completo", "VARCHAR(255)"),
        ("nome_mae", "VARCHAR(255)"),
        ("cpf", "VARCHAR(11)"),
        ("telefone_contato", "VARCHAR(20)"),
        ("data_nascimento", "DATETIME" if dialect_name == 'sqlite' else "TIMESTAMP"),
    ]
    
    colunas_transferencia = [
        ("tipo_transporte", "VARCHAR(50)"),
        ("status_ambulancia", "VARCHAR(50)"),
        ("data_solicitacao_ambulancia", "DATETIME" if dialect_name == 'sqlite' else "TIMESTAMP"),
        ("data_internacao", "DATETIME" if dialect_name == 'sqlite' else "TIMESTAMP"),
        ("observacoes_transferencia", "TEXT"),
        ("identificacao_ambulancia", "VARCHAR(50)"),
        ("distancia_km", "FLOAT" if dialect_name == 'sqlite' else "REAL"),
        ("tempo_estimado_min", "INTEGER"),
        ("data_entrega_destino", "DATETIME" if dialect_name == 'sqlite' else "TIMESTAMP"),
        ("data_alta", "DATETIME" if dialect_name == 'sqlite' else "TIMESTAMP"),
        ("observacoes_alta", "TEXT"),
        ("justificativa_negacao", "TEXT"),
    ]
    
    todas_colunas = colunas_lgpd + colunas_transferencia
    
    with engine.connect() as conn:
        # Verificar colunas existentes
        if dialect_name == 'sqlite':
            result = conn.execute(text("PRAGMA table_info(pacientes_regulacao)"))
            colunas_existentes = [row[1] for row in result]
        else:
            inspector = inspect(engine)
            colunas_existentes = [col['name'] for col in inspector.get_columns('pacientes_regulacao')]
        
        print(f"\n📊 Colunas existentes: {len(colunas_existentes)}")
        print(f"📊 Colunas a adicionar: {len(todas_colunas)}")
        
        # Adicionar colunas
        adicionadas = 0
        ja_existentes = 0
        
        for coluna, tipo in todas_colunas:
            if coluna in colunas_existentes:
                print(f"⚠️  Coluna '{coluna}' já existe")
                ja_existentes += 1
            else:
                try:
                    sql = f"ALTER TABLE pacientes_regulacao ADD COLUMN {coluna} {tipo}"
                    conn.execute(text(sql))
                    conn.commit()
                    print(f"✅ Coluna '{coluna}' adicionada ({tipo})")
                    adicionadas += 1
                except Exception as e:
                    print(f"❌ Erro ao adicionar coluna '{coluna}': {e}")
                    conn.rollback()
        
        print(f"\n{'='*60}")
        print(f"📊 RESUMO DA MIGRAÇÃO:")
        print(f"  ✅ Colunas adicionadas: {adicionadas}")
        print(f"  ⚠️  Colunas já existentes: {ja_existentes}")
        print(f"  📊 Total de colunas agora: {len(colunas_existentes) + adicionadas}")
        print(f"{'='*60}")
        
        # Verificar resultado final
        if dialect_name == 'sqlite':
            result = conn.execute(text("PRAGMA table_info(pacientes_regulacao)"))
            colunas_finais = [row[1] for row in result]
        else:
            inspector = inspect(engine)
            colunas_finais = [col['name'] for col in inspector.get_columns('pacientes_regulacao')]
        
        print(f"\n✅ Migração concluída!")
        print(f"📊 Total de colunas na tabela: {len(colunas_finais)}")
        
        # Verificar colunas críticas
        print(f"\n🔍 Verificando colunas críticas:")
        colunas_criticas = [
            'protocolo', 'status', 'nome_completo', 'cpf', 'especialidade',
            'cid', 'tipo_transporte', 'status_ambulancia', 'data_solicitacao_ambulancia'
        ]
        
        todas_ok = True
        for coluna in colunas_criticas:
            if coluna in colunas_finais:
                print(f"  ✅ {coluna}")
            else:
                print(f"  ❌ {coluna} - FALTANDO!")
                todas_ok = False
        
        if todas_ok:
            print(f"\n🎉 Todas as colunas críticas estão presentes!")
            print(f"✅ Banco de dados pronto para uso!")
        else:
            print(f"\n⚠️  Algumas colunas críticas estão faltando!")
            print(f"💡 Execute o script novamente ou verifique os erros acima")
        
except Exception as e:
    print(f"\n❌ Erro durante a migração:")
    print(f"   {str(e)}")
    print(f"\n💡 Dicas:")
    print(f"   1. Verifique se o banco de dados existe")
    print(f"   2. Verifique se a tabela 'pacientes_regulacao' existe")
    print(f"   3. Verifique permissões de escrita")
    print(f"   4. Verifique o arquivo .env")
    sys.exit(1)
