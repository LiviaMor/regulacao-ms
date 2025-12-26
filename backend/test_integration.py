#!/usr/bin/env python3
"""
Script de teste de integração para o Sistema de Regulação Autônoma SES-GO
"""

import requests
import json
import time
from datetime import datetime

# Configurações
BASE_URL = "http://localhost"
INGESTION_URL = f"{BASE_URL}:8001"
INTELLIGENCE_URL = f"{BASE_URL}:8002"
LOGISTICS_URL = f"{BASE_URL}:8003"

def test_health_checks():
    """Testa os health checks de todos os serviços"""
    print("🏥 Testando Health Checks...")
    
    services = [
        ("MS-Ingestion", f"{INGESTION_URL}/health"),
        ("MS-Intelligence", f"{INTELLIGENCE_URL}/health"),
        ("MS-Logistics", f"{LOGISTICS_URL}/health")
    ]
    
    for name, url in services:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {name}: OK")
            else:
                print(f"❌ {name}: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: {str(e)}")

def test_ingestion_service():
    """Testa o serviço de ingestão"""
    print("\n📊 Testando MS-Ingestion...")
    
    # Test dashboard endpoint
    try:
        response = requests.get(f"{INGESTION_URL}/dashboard/leitos", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Dashboard: {len(data.get('unidades_pressao', []))} unidades encontradas")
        else:
            print(f"❌ Dashboard: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Dashboard: {str(e)}")
    
    # Test pacientes endpoint
    try:
        response = requests.get(f"{INGESTION_URL}/pacientes?limit=5", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Pacientes: {len(data)} registros encontrados")
        else:
            print(f"❌ Pacientes: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Pacientes: {str(e)}")

def test_logistics_auth():
    """Testa autenticação no serviço de logística"""
    print("\n🔐 Testando MS-Logistics (Auth)...")
    
    # Test login
    login_data = {
        "email": "admin@sesgo.gov.br",
        "senha": "admin123"
    }
    
    try:
        response = requests.post(f"{LOGISTICS_URL}/login", json=login_data, timeout=10)
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            print("✅ Login: Sucesso")
            
            # Test authenticated endpoint
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(f"{LOGISTICS_URL}/me", headers=headers, timeout=10)
            if response.status_code == 200:
                user_data = response.json()
                print(f"✅ Token válido: {user_data.get('nome')}")
                return token
            else:
                print(f"❌ Token inválido: HTTP {response.status_code}")
        else:
            print(f"❌ Login falhou: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Login: {str(e)}")
    
    return None

def test_intelligence_service():
    """Testa o serviço de inteligência"""
    print("\n🤖 Testando MS-Intelligence...")
    
    # Test data for AI processing
    test_patient = {
        "protocolo": "TEST-" + str(int(time.time())),
        "especialidade": "CARDIOLOGIA",
        "cid": "I21.9",
        "cid_desc": "Infarto agudo do miocárdio",
        "prontuario_texto": "Paciente de 65 anos, sexo masculino, apresenta dor torácica intensa há 2 horas, com irradiação para braço esquerdo. ECG mostra elevação do segmento ST em derivações anteriores.",
        "historico_paciente": "HAS, Diabetes Mellitus tipo 2, tabagismo.",
        "prioridade_descricao": "Emergência"
    }
    
    try:
        response = requests.post(
            f"{INTELLIGENCE_URL}/processar-regulacao", 
            json=test_patient, 
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            print("✅ Processamento IA: Sucesso")
            
            # Verificar estrutura da resposta
            if "analise_decisoria" in data:
                analise = data["analise_decisoria"]
                print(f"   Score: {analise.get('score_prioridade')}/10")
                print(f"   Risco: {analise.get('classificacao_risco')}")
                print(f"   Unidade: {analise.get('unidade_destino_sugerida', 'N/A')[:50]}...")
            
            if "logistica" in data:
                logistica = data["logistica"]
                print(f"   Ambulância: {logistica.get('acionar_ambulancia')}")
                print(f"   Transporte: {logistica.get('tipo_transporte')}")
        else:
            print(f"❌ Processamento IA: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Processamento IA: {str(e)}")

def test_full_workflow(token):
    """Testa o fluxo completo de regulação"""
    if not token:
        print("\n⚠️  Pulando teste de fluxo completo (sem token)")
        return
    
    print("\n🔄 Testando Fluxo Completo...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Buscar fila de regulação
    try:
        response = requests.get(f"{LOGISTICS_URL}/fila-regulacao", headers=headers, timeout=10)
        if response.status_code == 200:
            fila = response.json()
            print(f"✅ Fila de regulação: {len(fila)} pacientes")
        else:
            print(f"❌ Fila de regulação: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Fila de regulação: {str(e)}")
    
    # 2. Dashboard do regulador
    try:
        response = requests.get(f"{LOGISTICS_URL}/dashboard-regulador", headers=headers, timeout=10)
        if response.status_code == 200:
            dashboard = response.json()
            stats = dashboard.get("estatisticas", {})
            print(f"✅ Dashboard regulador:")
            print(f"   Em regulação: {stats.get('em_regulacao', 0)}")
            print(f"   Autorizadas: {stats.get('autorizadas', 0)}")
            print(f"   Críticos: {stats.get('criticos', 0)}")
        else:
            print(f"❌ Dashboard regulador: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Dashboard regulador: {str(e)}")

def main():
    """Executa todos os testes"""
    print("🚀 Iniciando Testes de Integração")
    print("=" * 50)
    
    start_time = time.time()
    
    # Executar testes
    test_health_checks()
    test_ingestion_service()
    token = test_logistics_auth()
    test_intelligence_service()
    test_full_workflow(token)
    
    # Resumo
    end_time = time.time()
    duration = end_time - start_time
    
    print("\n" + "=" * 50)
    print(f"✅ Testes concluídos em {duration:.2f} segundos")
    print(f"🕒 Timestamp: {datetime.now().isoformat()}")
    print("\n📋 Próximos passos:")
    print("   1. Verificar logs dos serviços se houver falhas")
    print("   2. Testar o app React Native")
    print("   3. Configurar monitoramento em produção")

if __name__ == "__main__":
    main()