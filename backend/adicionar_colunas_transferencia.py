#!/usr/bin/env python3
"""
Script para adicionar colunas de transferência e ambulância no PostgreSQL
"""

import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv

load_dotenv()

# Configuração do banco
DB_CONFIG = {
    'dbname': 'regulacao_db',
    'user': 'postgres',
    'password': '1904',
    'host': 'localhost',
    'port': '5432'
}

def adicionar_colunas():
    """Adiciona colunas de transferência e ambulância"""
    
    try:
        # Conectar ao banco
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("✅ Conectado ao PostgreSQL")
        
        # Colunas a adicionar
        colunas = [
            ("tipo_transporte", "VARCHAR(50)"),
            ("status_ambulancia", "VARCHAR(50)"),
            ("data_solicitacao_ambulancia", "TIMESTAMP"),
            ("data_internacao", "TIMESTAMP"),
            ("observacoes_transferencia", "TEXT")
        ]
        
        for coluna, tipo in colunas:
            try:
                # Verificar se coluna já existe
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='pacientes_regulacao' 
                    AND column_name=%s
                """, (coluna,))
                
                if cursor.fetchone():
                    print(f"⚠️  Coluna '{coluna}' já existe")
                else:
                    # Adicionar coluna
                    cursor.execute(
                        sql.SQL("ALTER TABLE pacientes_regulacao ADD COLUMN {} {}").format(
                            sql.Identifier(coluna),
                            sql.SQL(tipo)
                        )
                    )
                    print(f"✅ Coluna '{coluna}' adicionada com sucesso")
            
            except Exception as e:
                print(f"❌ Erro ao adicionar coluna '{coluna}': {e}")
                conn.rollback()
                continue
        
        # Commit das alterações
        conn.commit()
        print("\n✅ Todas as colunas de transferência foram processadas!")
        
        # Verificar colunas finais
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name='pacientes_regulacao'
            ORDER BY ordinal_position
        """)
        
        print("\n📋 Colunas da tabela pacientes_regulacao:")
        for row in cursor.fetchall():
            print(f"  - {row[0]}: {row[1]}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Adicionando colunas de transferência e ambulância...")
    print("=" * 60)
    
    if adicionar_colunas():
        print("\n✅ Script executado com sucesso!")
    else:
        print("\n❌ Script falhou!")
