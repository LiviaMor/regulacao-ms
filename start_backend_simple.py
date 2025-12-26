#!/usr/bin/env python3
"""
Script simples para iniciar o backend com dados reais
"""

import subprocess
import sys
import time
import requests
import os
from pathlib import Path

def check_dependencies():
    """Verifica dependências básicas"""
    try:
        import fastapi
        import sqlalchemy
        import psycopg2
        print("✅ Dependências Python OK")
        return True
    except ImportError as e:
        print(f"❌ Dependência faltando: {e}")
        print("Execute: pip install -r requirements.txt")
        return False

def start_backend():
    """Inicia o backend unificado"""
    try:
        print("🚀 Iniciando backend unificado...")
        
        # Definir variáveis de ambiente
        env = os.environ.copy()
        env['DATABASE_URL'] = 'sqlite:///./regulacao.db'  # SQLite para simplicidade
        env['JWT_SECRET_KEY'] = 'regulacao_jwt_secret_key_development'
        
        # Iniciar processo
        process = subprocess.Popen([
            sys.executable, "backend/main_unified.py"
        ], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Aguardar inicialização
        print("⏳ Aguardando inicialização...")
        time.sleep(5)
        
        # Testar se está funcionando
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ Backend iniciado com sucesso!")
                return process
            else:
                print(f"❌ Backend respondeu com erro: {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"❌ Não foi possível conectar ao backend: {e}")
            return None
            
    except Exception as e:
        print(f"❌ Erro ao iniciar backend: {e}")
        return None

def load_data():
    """Carrega dados JSON"""
    try:
        print("📊 Carregando dados...")
        response = requests.post("http://localhost:8000/load-json-data", timeout=30)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Dados carregados: {data.get('message', 'OK')}")
            return True
        else:
            print(f"⚠️ Aviso no carregamento: {response.status_code}")
            return True  # Continuar mesmo com aviso
    except Exception as e:
        print(f"⚠️ Erro no carregamento: {e}")
        return True  # Continuar mesmo com erro

def test_endpoints():
    """Testa endpoints principais"""
    endpoints = [
        ("Dashboard", "http://localhost:8000/dashboard/leitos"),
        ("Health", "http://localhost:8000/health"),
        ("Login", "http://localhost:8000/login")
    ]
    
    print("\n🧪 Testando endpoints...")
    for name, url in endpoints:
        try:
            if name == "Login":
                # Testar login
                response = requests.post(url, json={
                    "email": "admin@sesgo.gov.br",
                    "senha": "admin123"
                }, timeout=5)
            else:
                response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                print(f"✅ {name}: OK")
            else:
                print(f"⚠️ {name}: {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: {e}")

def show_info():
    """Mostra informações do sistema"""
    print("\n" + "="*50)
    print("🎉 SISTEMA INICIADO COM SUCESSO!")
    print("="*50)
    
    print("\n📡 Endpoints disponíveis:")
    print("   • API: http://localhost:8000")
    print("   • Docs: http://localhost:8000/docs")
    print("   • Dashboard: http://localhost:8000/dashboard/leitos")
    print("   • Health: http://localhost:8000/health")
    
    print("\n🔐 Credenciais de teste:")
    print("   • Email: admin@sesgo.gov.br")
    print("   • Senha: admin123")
    
    print("\n📱 Frontend React Native:")
    print("   • Diretório: regulacao-app/")
    print("   • Comando: cd regulacao-app && npm start")
    
    print("\n⏹️ Pressione Ctrl+C para parar")

def main():
    """Função principal"""
    print("=== SISTEMA DE REGULAÇÃO SES-GO ===\n")
    
    # 1. Verificar dependências
    if not check_dependencies():
        return 1
    
    # 2. Iniciar backend
    backend_process = start_backend()
    if not backend_process:
        return 1
    
    try:
        # 3. Carregar dados
        load_data()
        
        # 4. Testar endpoints
        test_endpoints()
        
        # 5. Mostrar informações
        show_info()
        
        # 6. Manter rodando
        try:
            backend_process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Parando sistema...")
            backend_process.terminate()
            backend_process.wait()
            print("✅ Sistema parado")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n🛑 Interrompido pelo usuário")
        backend_process.terminate()
        backend_process.wait()
        return 0
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        backend_process.terminate()
        backend_process.wait()
        return 1

if __name__ == "__main__":
    exit(main())