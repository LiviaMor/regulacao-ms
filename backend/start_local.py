#!/usr/bin/env python3
"""
Script para iniciar os microserviços localmente (sem Docker)
Útil para desenvolvimento e quando Docker não está disponível
"""

import subprocess
import sys
import os
import time
import threading
from pathlib import Path

def install_requirements():
    """Instala dependências Python"""
    print("📦 Instalando dependências...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, cwd="backend")
        print("✅ Dependências instaladas")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao instalar dependências: {e}")
        return False
    return True

def setup_database():
    """Configura banco SQLite local para desenvolvimento"""
    print("🗄️ Configurando banco de dados local...")
    
    # Criar arquivo de ambiente local
    env_content = """
# Configuração local para desenvolvimento
DATABASE_URL=sqlite:///./regulacao_local.db
JWT_SECRET_KEY=dev_secret_key_change_in_production
OLLAMA_URL=http://localhost:11434
REDIS_URL=redis://localhost:6379
"""
    
    with open("backend/.env", "w") as f:
        f.write(env_content)
    
    print("✅ Configuração do banco criada")

def run_service(service_name, port, script_path):
    """Executa um microserviço em thread separada"""
    def run():
        try:
            print(f"🚀 Iniciando {service_name} na porta {port}...")
            env = os.environ.copy()
            env.update({
                'DATABASE_URL': 'sqlite:///./regulacao_local.db',
                'JWT_SECRET_KEY': 'dev_secret_key_change_in_production',
                'OLLAMA_URL': 'http://localhost:11434'
            })
            
            subprocess.run([
                sys.executable, "-m", "uvicorn", 
                "main:app", 
                "--host", "0.0.0.0", 
                "--port", str(port),
                "--reload"
            ], cwd=script_path, env=env)
        except Exception as e:
            print(f"❌ Erro ao iniciar {service_name}: {e}")
    
    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    return thread

def check_ollama():
    """Verifica se Ollama está rodando"""
    print("🔍 Verificando Ollama...")
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama está rodando")
            return True
    except:
        pass
    
    print("⚠️ Ollama não está rodando. Para usar IA:")
    print("   1. Instale: curl -fsSL https://ollama.ai/install.sh | sh")
    print("   2. Execute: ollama serve")
    print("   3. Baixe modelo: ollama pull llama3")
    return False

def main():
    """Função principal"""
    print("🏥 Sistema de Regulação SES-GO - Modo Local")
    print("=" * 50)
    
    # Verificar se estamos no diretório correto
    if not os.path.exists("backend"):
        print("❌ Execute este script do diretório raiz do projeto")
        sys.exit(1)
    
    # Instalar dependências
    if not install_requirements():
        sys.exit(1)
    
    # Configurar banco
    setup_database()
    
    # Verificar Ollama
    check_ollama()
    
    # Iniciar serviços
    services = [
        ("MS-Ingestion", 8001, "backend/ms-ingestion"),
        ("MS-Intelligence", 8002, "backend/ms-intelligence"), 
        ("MS-Logistics", 8003, "backend/ms-logistics")
    ]
    
    threads = []
    for name, port, path in services:
        if os.path.exists(path):
            thread = run_service(name, port, path)
            threads.append(thread)
            time.sleep(2)  # Aguardar entre inicializações
        else:
            print(f"⚠️ Diretório {path} não encontrado")
    
    print("\n🎉 Serviços iniciados!")
    print("\n📊 URLs dos serviços:")
    print("   MS-Ingestion: http://localhost:8001")
    print("   MS-Intelligence: http://localhost:8002") 
    print("   MS-Logistics: http://localhost:8003")
    
    print("\n📚 Documentação da API:")
    print("   http://localhost:8001/docs")
    print("   http://localhost:8002/docs")
    print("   http://localhost:8003/docs")
    
    print("\n🔧 Credenciais padrão:")
    print("   Email: admin@sesgo.gov.br")
    print("   Senha: admin123")
    
    print("\n⏹️ Pressione Ctrl+C para parar todos os serviços")
    
    try:
        # Manter script rodando
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Parando serviços...")
        sys.exit(0)

if __name__ == "__main__":
    main()