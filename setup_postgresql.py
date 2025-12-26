#!/usr/bin/env python3
"""
Script para configurar PostgreSQL no Windows para o projeto de regulação
"""

import subprocess
import sys
import time
import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def check_postgresql_installed():
    """Verifica se o PostgreSQL está instalado"""
    try:
        result = subprocess.run(['psql', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ PostgreSQL encontrado: {result.stdout.strip()}")
            return True
        else:
            print("❌ PostgreSQL não encontrado no PATH")
            return False
    except FileNotFoundError:
        print("❌ PostgreSQL não está instalado ou não está no PATH")
        return False

def check_postgresql_service():
    """Verifica se o serviço PostgreSQL está rodando"""
    try:
        # Verificar serviço no Windows
        result = subprocess.run([
            'sc', 'query', 'postgresql-x64-15'
        ], capture_output=True, text=True)
        
        if 'RUNNING' in result.stdout:
            print("✅ Serviço PostgreSQL está rodando")
            return True
        elif 'STOPPED' in result.stdout:
            print("⚠️ Serviço PostgreSQL está parado")
            return False
        else:
            # Tentar outros nomes de serviço comuns
            service_names = ['postgresql-x64-14', 'postgresql-x64-13', 'PostgreSQL']
            for service_name in service_names:
                result = subprocess.run([
                    'sc', 'query', service_name
                ], capture_output=True, text=True)
                
                if 'RUNNING' in result.stdout:
                    print(f"✅ Serviço PostgreSQL ({service_name}) está rodando")
                    return True
            
            print("❌ Nenhum serviço PostgreSQL encontrado rodando")
            return False
    except Exception as e:
        print(f"❌ Erro ao verificar serviço: {e}")
        return False

def start_postgresql_service():
    """Tenta iniciar o serviço PostgreSQL"""
    service_names = ['postgresql-x64-15', 'postgresql-x64-14', 'postgresql-x64-13', 'PostgreSQL']
    
    for service_name in service_names:
        try:
            print(f"🔄 Tentando iniciar serviço {service_name}...")
            result = subprocess.run([
                'net', 'start', service_name
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Serviço {service_name} iniciado com sucesso")
                time.sleep(3)  # Aguardar o serviço inicializar
                return True
            else:
                print(f"⚠️ Falha ao iniciar {service_name}: {result.stderr}")
        except Exception as e:
            print(f"❌ Erro ao tentar iniciar {service_name}: {e}")
    
    return False

def test_connection(host='localhost', port=5432, user='postgres', password=None):
    """Testa conexão com PostgreSQL"""
    try:
        if password is None:
            # Tentar senhas comuns
            common_passwords = ['postgres', 'admin', '123456', '', 'password']
            for pwd in common_passwords:
                try:
                    conn = psycopg2.connect(
                        host=host,
                        port=port,
                        user=user,
                        password=pwd,
                        database='postgres'
                    )
                    conn.close()
                    print(f"✅ Conexão bem-sucedida com senha: {'(vazia)' if pwd == '' else pwd}")
                    return pwd
                except psycopg2.OperationalError:
                    continue
            
            print("❌ Não foi possível conectar com senhas comuns")
            return None
        else:
            conn = psycopg2.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database='postgres'
            )
            conn.close()
            print("✅ Conexão bem-sucedida")
            return password
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return None

def create_database_and_user(admin_password):
    """Cria o banco de dados e usuário para o projeto"""
    try:
        # Conectar como admin
        conn = psycopg2.connect(
            host='localhost',
            port=5432,
            user='postgres',
            password=admin_password,
            database='postgres'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Verificar se usuário já existe
        cursor.execute("SELECT 1 FROM pg_roles WHERE rolname='regulacao_user'")
        user_exists = cursor.fetchone()
        
        if not user_exists:
            print("🔄 Criando usuário regulacao_user...")
            cursor.execute("CREATE USER regulacao_user WITH PASSWORD 'regulacao_pass'")
            print("✅ Usuário criado")
        else:
            print("✅ Usuário regulacao_user já existe")
        
        # Verificar se banco já existe
        cursor.execute("SELECT 1 FROM pg_database WHERE datname='regulacao_db'")
        db_exists = cursor.fetchone()
        
        if not db_exists:
            print("🔄 Criando banco de dados regulacao_db...")
            cursor.execute("CREATE DATABASE regulacao_db OWNER regulacao_user")
            print("✅ Banco de dados criado")
        else:
            print("✅ Banco de dados regulacao_db já existe")
        
        # Dar permissões
        cursor.execute("GRANT ALL PRIVILEGES ON DATABASE regulacao_db TO regulacao_user")
        print("✅ Permissões concedidas")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar banco/usuário: {e}")
        return False

def test_project_connection():
    """Testa conexão com as credenciais do projeto"""
    try:
        conn = psycopg2.connect(
            host='localhost',
            port=5432,
            user='regulacao_user',
            password='regulacao_pass',
            database='regulacao_db'
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT version()")
        version = cursor.fetchone()
        print(f"✅ Conexão do projeto OK: {version[0]}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro na conexão do projeto: {e}")
        return False

def create_tables():
    """Cria as tabelas do projeto"""
    try:
        # Importar e executar create_tables
        sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
        from shared.database import create_tables as create_project_tables
        
        print("🔄 Criando tabelas do projeto...")
        create_project_tables()
        print("✅ Tabelas criadas com sucesso")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")
        return False

def main():
    """Função principal"""
    print("=== CONFIGURAÇÃO DO POSTGRESQL PARA REGULAÇÃO SES-GO ===\n")
    
    # 1. Verificar se PostgreSQL está instalado
    print("1. Verificando instalação do PostgreSQL...")
    if not check_postgresql_installed():
        print("\n❌ ERRO: PostgreSQL não está instalado!")
        print("\nPara instalar no Windows:")
        print("1. Baixe de: https://www.postgresql.org/download/windows/")
        print("2. Execute o instalador")
        print("3. Anote a senha do usuário 'postgres'")
        print("4. Execute este script novamente")
        return 1
    print()
    
    # 2. Verificar se o serviço está rodando
    print("2. Verificando serviço PostgreSQL...")
    if not check_postgresql_service():
        print("🔄 Tentando iniciar o serviço...")
        if not start_postgresql_service():
            print("\n❌ ERRO: Não foi possível iniciar o PostgreSQL!")
            print("\nTente manualmente:")
            print("1. Abra 'Serviços' do Windows (services.msc)")
            print("2. Procure por 'PostgreSQL' ou 'postgresql-x64-XX'")
            print("3. Clique com botão direito > Iniciar")
            return 1
    print()
    
    # 3. Testar conexão
    print("3. Testando conexão com PostgreSQL...")
    admin_password = test_connection()
    if admin_password is None:
        print("\n❌ ERRO: Não foi possível conectar ao PostgreSQL!")
        print("\nVerifique:")
        print("1. Se o serviço está rodando")
        print("2. A senha do usuário 'postgres'")
        print("3. Se a porta 5432 está livre")
        
        # Solicitar senha manualmente
        manual_password = input("\nDigite a senha do usuário 'postgres' (ou Enter para pular): ").strip()
        if manual_password:
            admin_password = test_connection(password=manual_password)
            if admin_password is None:
                return 1
        else:
            return 1
    print()
    
    # 4. Criar banco e usuário
    print("4. Configurando banco de dados do projeto...")
    if not create_database_and_user(admin_password):
        return 1
    print()
    
    # 5. Testar conexão do projeto
    print("5. Testando conexão do projeto...")
    if not test_project_connection():
        return 1
    print()
    
    # 6. Criar tabelas
    print("6. Criando tabelas...")
    if not create_tables():
        return 1
    print()
    
    # 7. Sucesso!
    print("🎉 POSTGRESQL CONFIGURADO COM SUCESSO!")
    print("\n📋 Informações da configuração:")
    print("   • Host: localhost")
    print("   • Porta: 5432")
    print("   • Banco: regulacao_db")
    print("   • Usuário: regulacao_user")
    print("   • Senha: regulacao_pass")
    
    print("\n🚀 Próximos passos:")
    print("   1. Execute: python backend/main_unified.py")
    print("   2. Ou execute: python start_with_data.py")
    print("   3. Acesse: http://localhost:8000/docs")
    
    return 0

if __name__ == "__main__":
    exit(main())