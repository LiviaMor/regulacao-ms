#!/usr/bin/env python3
"""
Script para iniciar o sistema com dados reais carregados
"""

import subprocess
import sys
import time
import requests
import json
from pathlib import Path

def check_dependencies():
    """Verifica se as dependências estão instaladas"""
    required_packages = ['pandas', 'requests', 'fastapi', 'uvicorn']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Dependências faltando: {', '.join(missing_packages)}")
        print("Instale com: pip install " + " ".join(missing_packages))
        return False
    
    return True

def check_data_files():
    """Verifica se os arquivos de dados existem"""
    required_files = [
        'dados_em_regulacao.json',
        'dados_admitidos.json', 
        'dados_alta.json',
        'dados_em_transito.json'
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Arquivos de dados faltando: {', '.join(missing_files)}")
        return False
    
    print("✅ Todos os arquivos de dados encontrados")
    return True

def start_backend():
    """Inicia o backend"""
    print("🚀 Iniciando backend...")
    
    try:
        # Tentar iniciar o backend unificado
        process = subprocess.Popen([
            sys.executable, "backend/main_unified.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Aguardar um pouco para o servidor iniciar
        time.sleep(5)
        
        # Verificar se está funcionando
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ Backend iniciado com sucesso")
                return process
            else:
                print("❌ Backend não está respondendo corretamente")
                process.terminate()
                return None
        except:
            print("❌ Não foi possível conectar ao backend")
            process.terminate()
            return None
            
    except Exception as e:
        print(f"❌ Erro ao iniciar backend: {e}")
        return None

def load_data():
    """Carrega os dados JSON na API"""
    print("📊 Carregando dados...")
    
    try:
        response = requests.post("http://localhost:8000/load-json-data", timeout=60)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Dados carregados: {data.get('total_registros', 0)} registros")
            return True
        else:
            print(f"⚠️ Aviso no carregamento: {response.status_code}")
            return True  # Continuar mesmo com aviso
    except Exception as e:
        print(f"⚠️ Erro no carregamento (continuando): {e}")
        return True  # Continuar mesmo com erro

def test_dashboard():
    """Testa o dashboard"""
    print("🧪 Testando dashboard...")
    
    try:
        response = requests.get("http://localhost:8000/dashboard/leitos", timeout=10)
        if response.status_code == 200:
            data = response.json()
            
            total_registros = 0
            for status in data.get('status_summary', []):
                total_registros += status.get('count', 0)
            
            print(f"✅ Dashboard funcionando: {total_registros} registros")
            print(f"   Fonte: {data.get('fonte', 'N/A')}")
            
            # Mostrar algumas estatísticas
            unidades = data.get('unidades_pressao', [])
            if unidades:
                print(f"   🏥 {len(unidades)} unidades com pacientes em fila")
                top_unidade = unidades[0] if unidades else None
                if top_unidade:
                    print(f"   📈 Maior pressão: {top_unidade['unidade_executante_desc']} ({top_unidade['pacientes_em_fila']} pacientes)")
            
            return True
        else:
            print(f"❌ Dashboard com erro: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao testar dashboard: {e}")
        return False

def main():
    """Função principal"""
    print("=== INICIANDO SISTEMA DE REGULAÇÃO COM DADOS REAIS ===\n")
    
    # 1. Verificar dependências
    print("1. Verificando dependências...")
    if not check_dependencies():
        return 1
    print("✅ Dependências OK\n")
    
    # 2. Verificar arquivos de dados
    print("2. Verificando arquivos de dados...")
    if not check_data_files():
        return 1
    print()
    
    # 3. Processar dados (teste rápido)
    print("3. Testando processamento de dados...")
    try:
        from backend.data_processor import SESGoDataProcessor
        processor = SESGoDataProcessor(".")
        dashboard_data = processor.generate_dashboard_data()
        print(f"✅ Processamento OK: {dashboard_data.get('total_registros', 0)} registros")
    except Exception as e:
        print(f"❌ Erro no processamento: {e}")
        return 1
    print()
    
    # 4. Iniciar backend
    print("4. Iniciando backend...")
    backend_process = start_backend()
    if not backend_process:
        return 1
    print()
    
    try:
        # 5. Carregar dados
        print("5. Carregando dados na API...")
        if not load_data():
            print("⚠️ Continuando sem carregar dados no banco...")
        print()
        
        # 6. Testar dashboard
        print("6. Testando dashboard...")
        if not test_dashboard():
            print("❌ Dashboard com problemas")
            return 1
        print()
        
        # 7. Sucesso!
        print("🎉 SISTEMA INICIADO COM SUCESSO!")
        print("\n📋 Informações importantes:")
        print("   • API Backend: http://localhost:8000")
        print("   • Documentação: http://localhost:8000/docs")
        print("   • Dashboard: http://localhost:8000/dashboard/leitos")
        print("   • Health Check: http://localhost:8000/health")
        
        print("\n🚀 Próximos passos:")
        print("   1. Teste a API em http://localhost:8000/docs")
        print("   2. Inicie o app React Native:")
        print("      cd regulacao-app")
        print("      npm start")
        print("   3. Pressione Ctrl+C para parar o servidor")
        
        # Manter o servidor rodando
        print("\n⏳ Servidor rodando... (Pressione Ctrl+C para parar)")
        try:
            backend_process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Parando servidor...")
            backend_process.terminate()
            backend_process.wait()
            print("✅ Servidor parado")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n🛑 Interrompido pelo usuário")
        if backend_process:
            backend_process.terminate()
            backend_process.wait()
        return 0
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        if backend_process:
            backend_process.terminate()
            backend_process.wait()
        return 1

if __name__ == "__main__":
    exit(main())