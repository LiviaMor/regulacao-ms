#!/usr/bin/env python3
"""
Script de inicialização simplificado do Sistema de Regulação SES-GO
Funciona sem Docker, ideal para desenvolvimento e demonstração
"""

import subprocess
import sys
import os
import time
import threading
import requests
from datetime import datetime

def print_header(title):
    print("\n" + "="*60)
    print(f"🏥 {title}")
    print("="*60)

def print_step(step, description):
    print(f"\n📋 PASSO {step}: {description}")
    print("-" * 50)

def install_requirements():
    """Instala dependências básicas"""
    print("📦 Instalando dependências...")
    try:
        # Instalar apenas dependências essenciais
        essential_packages = [
            "fastapi==0.104.1",
            "uvicorn[standard]==0.24.0", 
            "sqlalchemy==2.0.23",
            "pydantic==2.5.0",
            "python-jose[cryptography]==3.3.0",
            "passlib[bcrypt]==1.7.4",
            "python-multipart==0.0.6",
            "requests==2.31.0",
            "Pillow==10.1.0"
        ]
        
        for package in essential_packages:
            print(f"   Instalando {package}...")
            subprocess.run([sys.executable, "-m", "pip", "install", package], 
                          check=True, capture_output=True)
        
        print("✅ Dependências essenciais instaladas")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao instalar dependências: {e}")
        print("   Tentando continuar sem algumas dependências...")
        return True  # Continuar mesmo com erro

def setup_environment():
    """Configura ambiente local"""
    print("⚙️ Configurando ambiente...")
    
    # Criar diretório backend se não existir
    os.makedirs("backend", exist_ok=True)
    
    # Criar arquivo de ambiente
    env_content = """DATABASE_URL=sqlite:///./regulacao_demo.db
JWT_SECRET_KEY=demo_secret_key_change_in_production
OLLAMA_URL=http://localhost:11434
"""
    
    with open("backend/.env", "w") as f:
        f.write(env_content)
    
    print("✅ Ambiente configurado")

def create_simple_app():
    """Cria aplicação simplificada"""
    print("🔧 Criando aplicação simplificada...")
    
    app_code = '''
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import json
import os

app = FastAPI(title="Sistema de Regulação SES-GO - Demo", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PacienteInput(BaseModel):
    protocolo: str
    especialidade: str = "CLINICA MÉDICA"
    cid: str = "Z00.0"
    cid_desc: str = "Exame médico geral"
    prontuario_texto: str = ""
    historico_paciente: str = ""
    prioridade_descricao: str = "Normal"

class LoginData(BaseModel):
    email: str
    senha: str

@app.get("/")
async def root():
    return {
        "service": "Sistema de Regulação SES-GO - Demo",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.get("/dashboard/leitos")
async def dashboard_leitos():
    return {
        "status_summary": [
            {"status": "EM_REGULACAO", "count": 25},
            {"status": "INTERNACAO_AUTORIZADA", "count": 8},
            {"status": "INTERNADA", "count": 156},
            {"status": "COM_ALTA", "count": 43}
        ],
        "unidades_pressao": [
            {
                "unidade_executante_desc": "HOSPITAL ESTADUAL DR ALBERTO RASSI HGG",
                "cidade": "GOIANIA",
                "pacientes_em_fila": 12
            },
            {
                "unidade_executante_desc": "HOSPITAL DE URGENCIAS DE GOIAS",
                "cidade": "GOIANIA", 
                "pacientes_em_fila": 8
            },
            {
                "unidade_executante_desc": "HOSPITAL ESTADUAL DE FORMOSA",
                "cidade": "FORMOSA",
                "pacientes_em_fila": 5
            }
        ],
        "ultima_atualizacao": datetime.utcnow().isoformat()
    }

@app.post("/processar-regulacao")
async def processar_regulacao(paciente: PacienteInput):
    # Simular processamento IA
    import time
    time.sleep(1)  # Simular tempo de processamento
    
    # Determinar risco baseado no CID
    risco = "VERDE"
    score = 3
    if "I21" in paciente.cid or "emergencia" in paciente.prioridade_descricao.lower():
        risco = "VERMELHO"
        score = 9
    elif "urgente" in paciente.prioridade_descricao.lower():
        risco = "AMARELO" 
        score = 6
    
    return {
        "analise_decisoria": {
            "score_prioridade": score,
            "classificacao_risco": risco,
            "unidade_destino_sugerida": "HOSPITAL ESTADUAL DR ALBERTO RASSI HGG",
            "justificativa_clinica": f"Paciente com {paciente.especialidade} - {paciente.cid_desc}. Análise baseada em protocolos padrão."
        },
        "logistica": {
            "acionar_ambulancia": risco in ["VERMELHO", "AMARELO"],
            "tipo_transporte": "USA" if risco == "VERMELHO" else "USB",
            "previsao_vaga_h": "1-2 horas" if risco == "VERMELHO" else "2-4 horas"
        },
        "protocolo_especial": {
            "tipo": "UTI" if risco == "VERMELHO" else "NORMAL",
            "instrucoes_imediatas": "Monitorização contínua" if risco == "VERMELHO" else "Cuidados padrão"
        },
        "metadata": {
            "tempo_processamento": 1.0,
            "biobert_usado": False,
            "timestamp": datetime.utcnow().isoformat()
        }
    }

@app.post("/login")
async def login(dados: LoginData):
    if dados.email == "admin@sesgo.gov.br" and dados.senha == "admin123":
        return {
            "access_token": "demo_token_12345",
            "token_type": "bearer",
            "user_info": {
                "id": 1,
                "email": dados.email,
                "nome": "Administrador Demo",
                "tipo_usuario": "ADMIN"
            }
        }
    raise HTTPException(status_code=401, detail="Credenciais inválidas")

@app.post("/transferencia")
async def transferencia(data: dict):
    return {
        "message": "Transferência autorizada com sucesso",
        "protocolo": data.get("protocolo"),
        "unidade_destino": data.get("unidade_destino"),
        "autorizado_por": "Administrador Demo"
    }

@app.get("/fila-regulacao")
async def fila_regulacao():
    return [
        {
            "protocolo": f"DEMO-{i:03d}",
            "data_solicitacao": datetime.utcnow().isoformat(),
            "especialidade": ["CARDIOLOGIA", "ORTOPEDIA", "NEUROLOGIA"][i % 3],
            "cidade_origem": ["GOIANIA", "ANAPOLIS", "FORMOSA"][i % 3],
            "unidade_solicitante": f"Hospital Municipal {i}",
            "score_prioridade": (i % 8) + 2,
            "classificacao_risco": ["VERDE", "AMARELO", "VERMELHO"][i % 3],
            "justificativa_tecnica": f"Paciente necessita avaliação em {['CARDIOLOGIA', 'ORTOPEDIA', 'NEUROLOGIA'][i % 3]}"
        }
        for i in range(1, 6)
    ]

@app.get("/dashboard-regulador")
async def dashboard_regulador():
    return {
        "estatisticas": {
            "em_regulacao": 25,
            "autorizadas": 8,
            "internadas": 156,
            "criticos": 3,
            "tempo_medio_regulacao_h": 1.8
        },
        "usuario": {
            "nome": "Administrador Demo",
            "tipo": "ADMIN"
        },
        "ultima_atualizacao": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
    
    with open("backend/app_demo.py", "w", encoding="utf-8") as f:
        f.write(app_code)
    
    print("✅ Aplicação demo criada")

def start_api_server():
    """Inicia servidor da API"""
    def run_server():
        try:
            print("🚀 Iniciando servidor da API na porta 8000...")
            subprocess.run([
                sys.executable, "backend/app_demo.py"
            ], cwd=".")
        except Exception as e:
            print(f"❌ Erro ao iniciar servidor: {e}")
    
    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()
    return thread

def test_api():
    """Testa se a API está funcionando"""
    print("🧪 Testando API...")
    
    max_attempts = 10
    for attempt in range(max_attempts):
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ API está funcionando!")
                return True
        except:
            pass
        
        if attempt < max_attempts - 1:
            print(f"   Tentativa {attempt + 1}/{max_attempts}... aguardando...")
            time.sleep(2)
    
    print("❌ API não respondeu após várias tentativas")
    return False

def main():
    """Função principal"""
    print_header("SISTEMA DE REGULAÇÃO SES-GO - DEMO SIMPLIFICADO")
    print("🎯 Versão simplificada para demonstração e desenvolvimento")
    print(f"⏰ Iniciado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    print_step(1, "PREPARAÇÃO DO AMBIENTE")
    install_requirements()
    setup_environment()
    create_simple_app()
    
    print_step(2, "INICIANDO SERVIDOR")
    api_thread = start_api_server()
    
    # Aguardar servidor iniciar
    time.sleep(3)
    
    print_step(3, "TESTANDO CONECTIVIDADE")
    if test_api():
        print_header("SISTEMA INICIADO COM SUCESSO!")
        print("\n🌐 ENDPOINTS DISPONÍVEIS:")
        print("   • Dashboard Público: http://localhost:8000/dashboard/leitos")
        print("   • Processamento IA: http://localhost:8000/processar-regulacao")
        print("   • Login: http://localhost:8000/login")
        print("   • Documentação: http://localhost:8000/docs")
        
        print("\n🔐 CREDENCIAIS DE TESTE:")
        print("   • Email: admin@sesgo.gov.br")
        print("   • Senha: admin123")
        
        print("\n📱 PRÓXIMOS PASSOS:")
        print("   1. Abrir o app React Native:")
        print("      cd regulacao-app && npm install && npm start")
        print("   2. Testar endpoints no navegador")
        print("   3. Executar: python demo_completo.py")
        
        print("\n⏹️ Pressione Ctrl+C para parar o servidor")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Parando servidor...")
            sys.exit(0)
    else:
        print("❌ Falha ao iniciar o sistema")
        sys.exit(1)

if __name__ == "__main__":
    main()