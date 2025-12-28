#!/usr/bin/env python3
"""
Script para adicionar colunas de anexos ao banco de dados
Suporta PostgreSQL (produção) e SQLite (desenvolvimento)
"""

import os
import sys
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./regulacao.db")

def adicionar_colunas_postgres():
    """Adiciona colunas no PostgreSQL"""
    import psycopg2
    
    # Extrair conexão do DATABASE_URL
    # postgresql://postgres:1904@localhost:5432/regulacao_db
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    colunas = [
        ("anexo_filename", "VARCHAR(255)"),
        ("anexo_tipo", "VARCHAR(100)"),
        ("anexo_tamanho", "INTEGER"),
        ("anexo_base64", "TEXT"),
        ("anexo_path", "VARCHAR(500)"),
        ("anexo_texto_ocr", "TEXT"),
        ("anexo_analise_biobert", "TEXT"),
        ("anexo_analise_llama", "TEXT"),
        ("anexo_confianca_ia", "FLOAT"),
        ("anexo_alertas", "TEXT"),
        ("anexo_processado_em", "TIMESTAMP"),
    ]
    
    print("=" * 60)
    print("ADICIONANDO COLUNAS DE ANEXOS - PostgreSQL")
    print("=" * 60)
    
    for coluna, tipo in colunas:
        try:
            sql = f"ALTER TABLE pacientes_regulacao ADD COLUMN IF NOT EXISTS {coluna} {tipo};"
            cursor.execute(sql)
            print(f"✅ Coluna '{coluna}' adicionada/verificada")
        except Exception as e:
            print(f"⚠️ Coluna '{coluna}': {e}")
    
    conn.commit()
    
    # Verificar colunas
    cursor.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'pacientes_regulacao' 
        AND column_name LIKE 'anexo_%'
        ORDER BY ordinal_position
    """)
    
    print("\n📋 Colunas de anexo no banco:")
    for row in cursor.fetchall():
        print(f"   - {row[0]}: {row[1]}")
    
    cursor.close()
    conn.close()
    print("\n✅ Migração PostgreSQL concluída!")


def adicionar_colunas_sqlite():
    """Adiciona colunas no SQLite"""
    import sqlite3
    
    db_path = DATABASE_URL.replace("sqlite:///", "")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    colunas = [
        ("anexo_filename", "TEXT"),
        ("anexo_tipo", "TEXT"),
        ("anexo_tamanho", "INTEGER"),
        ("anexo_base64", "TEXT"),
        ("anexo_path", "TEXT"),
        ("anexo_texto_ocr", "TEXT"),
        ("anexo_analise_biobert", "TEXT"),
        ("anexo_analise_llama", "TEXT"),
        ("anexo_confianca_ia", "REAL"),
        ("anexo_alertas", "TEXT"),
        ("anexo_processado_em", "TIMESTAMP"),
    ]
    
    print("=" * 60)
    print("ADICIONANDO COLUNAS DE ANEXOS - SQLite")
    print("=" * 60)
    
    # Verificar colunas existentes
    cursor.execute("PRAGMA table_info(pacientes_regulacao)")
    colunas_existentes = [row[1] for row in cursor.fetchall()]
    
    for coluna, tipo in colunas:
        if coluna not in colunas_existentes:
            try:
                sql = f"ALTER TABLE pacientes_regulacao ADD COLUMN {coluna} {tipo};"
                cursor.execute(sql)
                print(f"✅ Coluna '{coluna}' adicionada")
            except Exception as e:
                print(f"⚠️ Coluna '{coluna}': {e}")
        else:
            print(f"ℹ️ Coluna '{coluna}' já existe")
    
    conn.commit()
    
    # Verificar colunas
    cursor.execute("PRAGMA table_info(pacientes_regulacao)")
    print("\n📋 Colunas de anexo no banco:")
    for row in cursor.fetchall():
        if 'anexo' in row[1]:
            print(f"   - {row[1]}: {row[2]}")
    
    cursor.close()
    conn.close()
    print("\n✅ Migração SQLite concluída!")


def adicionar_colunas_docker():
    """Adiciona colunas no PostgreSQL dentro do Docker"""
    import subprocess
    
    colunas = [
        ("anexo_filename", "VARCHAR(255)"),
        ("anexo_tipo", "VARCHAR(100)"),
        ("anexo_tamanho", "INTEGER"),
        ("anexo_base64", "TEXT"),
        ("anexo_path", "VARCHAR(500)"),
        ("anexo_texto_ocr", "TEXT"),
        ("anexo_analise_biobert", "TEXT"),
        ("anexo_analise_llama", "TEXT"),
        ("anexo_confianca_ia", "FLOAT"),
        ("anexo_alertas", "TEXT"),
        ("anexo_processado_em", "TIMESTAMP"),
    ]
    
    print("=" * 60)
    print("ADICIONANDO COLUNAS DE ANEXOS - Docker PostgreSQL")
    print("=" * 60)
    
    for coluna, tipo in colunas:
        sql = f"ALTER TABLE pacientes_regulacao ADD COLUMN IF NOT EXISTS {coluna} {tipo};"
        cmd = f'docker exec regulacao_postgres psql -U postgres -d regulacao_db -c "{sql}"'
        
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Coluna '{coluna}' adicionada/verificada")
            else:
                print(f"⚠️ Coluna '{coluna}': {result.stderr}")
        except Exception as e:
            print(f"❌ Erro: {e}")
    
    # Verificar colunas
    cmd = '''docker exec regulacao_postgres psql -U postgres -d regulacao_db -c "SELECT column_name FROM information_schema.columns WHERE table_name = 'pacientes_regulacao' AND column_name LIKE 'anexo_%' ORDER BY ordinal_position;"'''
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    print("\n📋 Colunas de anexo no Docker:")
    print(result.stdout)
    
    print("\n✅ Migração Docker concluída!")


def main():
    print("\n🔧 MIGRAÇÃO: Colunas de Anexos para Documentos Médicos")
    print(f"📍 DATABASE_URL: {DATABASE_URL[:50]}...")
    
    if "postgresql" in DATABASE_URL:
        adicionar_colunas_postgres()
    else:
        adicionar_colunas_sqlite()
    
    # Também executar no Docker se estiver rodando
    try:
        import subprocess
        result = subprocess.run("docker ps --filter name=regulacao_postgres --format '{{.Names}}'", 
                              shell=True, capture_output=True, text=True)
        if "regulacao_postgres" in result.stdout:
            print("\n" + "=" * 60)
            print("Detectado container Docker, executando migração...")
            adicionar_colunas_docker()
    except:
        pass


if __name__ == "__main__":
    main()
