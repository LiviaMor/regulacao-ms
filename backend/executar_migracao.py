"""
Script para executar migração SQL no PostgreSQL
Adiciona campos LGPD à tabela pacientes_regulacao
"""

import os
import sys
sys.path.insert(0, '.')

from sqlalchemy import create_engine, text
from shared.database import DATABASE_URL

def executar_migracao():
    """Executa o script de migração SQL"""
    
    print("🔄 Iniciando migração do banco de dados...")
    print(f"📊 Banco: {DATABASE_URL}")
    
    try:
        # Conectar ao banco
        engine = create_engine(DATABASE_URL)
        
        # Ler arquivo SQL
        with open('migration_add_lgpd_fields.sql', 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        # Executar migração
        with engine.connect() as conn:
            # Dividir em comandos individuais
            comandos = [cmd.strip() for cmd in sql_script.split(';') if cmd.strip()]
            
            for i, comando in enumerate(comandos, 1):
                if comando and not comando.startswith('--'):
                    print(f"\n📝 Executando comando {i}/{len(comandos)}...")
                    try:
                        result = conn.execute(text(comando))
                        conn.commit()
                        
                        # Se for SELECT, mostrar resultado
                        if comando.strip().upper().startswith('SELECT'):
                            rows = result.fetchall()
                            if rows:
                                print(f"   Resultado: {rows[0]}")
                        else:
                            print(f"   ✅ OK")
                    except Exception as e:
                        print(f"   ⚠️ Aviso: {e}")
                        # Continuar mesmo com erros (ex: coluna já existe)
        
        print("\n✅ Migração concluída com sucesso!")
        print("\n📋 Verificando estrutura da tabela...")
        
        # Verificar colunas
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'pacientes_regulacao'
                AND column_name IN ('nome_completo', 'nome_mae', 'cpf', 'telefone_contato', 'data_nascimento')
                ORDER BY column_name
            """))
            
            colunas = result.fetchall()
            if colunas:
                print("\n✅ Novas colunas criadas:")
                for col in colunas:
                    print(f"   - {col[0]}: {col[1]} (nullable: {col[2]})")
            else:
                print("\n⚠️ Nenhuma coluna nova encontrada")
        
    except Exception as e:
        print(f"\n❌ Erro na migração: {e}")
        return False
    
    return True

if __name__ == "__main__":
    sucesso = executar_migracao()
    sys.exit(0 if sucesso else 1)
