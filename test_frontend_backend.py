#!/usr/bin/env python3
"""
Script para testar a integração frontend-backend
"""

import requests
import json
import time

def test_backend_endpoints():
    """Testa todos os endpoints do backend"""
    base_url = "http://localhost:8000"
    
    tests = [
        {
            "name": "Health Check",
            "method": "GET",
            "url": f"{base_url}/health",
            "expected_status": 200
        },
        {
            "name": "Dashboard Leitos",
            "method": "GET", 
            "url": f"{base_url}/dashboard/leitos",
            "expected_status": 200
        },
        {
            "name": "Login Admin",
            "method": "POST",
            "url": f"{base_url}/login",
            "data": {
                "email": "admin@sesgo.gov.br",
                "senha": "admin123"
            },
            "expected_status": 200
        },
        {
            "name": "Carregar Dados JSON",
            "method": "POST",
            "url": f"{base_url}/load-json-data",
            "expected_status": 200
        }
    ]
    
    print("🧪 Testando endpoints do backend...\n")
    
    token = None
    
    for test in tests:
        try:
            print(f"Testando: {test['name']}")
            
            if test['method'] == 'GET':
                response = requests.get(test['url'], timeout=10)
            elif test['method'] == 'POST':
                headers = {'Content-Type': 'application/json'}
                if token and 'Authorization' in test.get('headers', {}):
                    headers['Authorization'] = f"Bearer {token}"
                
                data = test.get('data', {})
                response = requests.post(test['url'], json=data, headers=headers, timeout=30)
            
            if response.status_code == test['expected_status']:
                print(f"✅ {test['name']}: OK")
                
                # Salvar token do login
                if test['name'] == 'Login Admin':
                    result = response.json()
                    token = result.get('access_token')
                    print(f"   Token obtido: {token[:20]}...")
                
                # Mostrar dados do dashboard
                if test['name'] == 'Dashboard Leitos':
                    result = response.json()
                    status_summary = result.get('status_summary', [])
                    unidades = result.get('unidades_pressao', [])
                    print(f"   Status: {len(status_summary)} tipos")
                    print(f"   Unidades: {len(unidades)} hospitais")
                    if unidades:
                        print(f"   Top: {unidades[0].get('unidade_executante_desc', 'N/A')}")
                
            else:
                print(f"❌ {test['name']}: {response.status_code}")
                print(f"   Resposta: {response.text[:100]}...")
                
        except Exception as e:
            print(f"❌ {test['name']}: Erro - {e}")
        
        print()
    
    return token

def test_authenticated_endpoints(token):
    """Testa endpoints que precisam de autenticação"""
    if not token:
        print("⚠️ Sem token, pulando testes autenticados")
        return
    
    base_url = "http://localhost:8000"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    auth_tests = [
        {
            "name": "Fila de Regulação",
            "method": "GET",
            "url": f"{base_url}/fila-regulacao"
        },
        {
            "name": "Dashboard Regulador", 
            "method": "GET",
            "url": f"{base_url}/dashboard-regulador"
        },
        {
            "name": "Processar Regulação IA",
            "method": "POST",
            "url": f"{base_url}/processar-regulacao",
            "data": {
                "protocolo": "TEST-001",
                "especialidade": "CARDIOLOGIA",
                "cid": "I21.9",
                "cid_desc": "Infarto agudo do miocárdio",
                "prontuario_texto": "Paciente com dor torácica há 2 horas",
                "historico_paciente": "Hipertensão arterial",
                "prioridade_descricao": "Alta"
            }
        }
    ]
    
    print("🔐 Testando endpoints autenticados...\n")
    
    for test in auth_tests:
        try:
            print(f"Testando: {test['name']}")
            
            if test['method'] == 'GET':
                response = requests.get(test['url'], headers=headers, timeout=10)
            elif test['method'] == 'POST':
                data = test.get('data', {})
                response = requests.post(test['url'], json=data, headers=headers, timeout=30)
            
            if response.status_code == 200:
                print(f"✅ {test['name']}: OK")
                
                result = response.json()
                
                # Mostrar detalhes específicos
                if test['name'] == 'Fila de Regulação':
                    if isinstance(result, list):
                        print(f"   Pacientes na fila: {len(result)}")
                
                elif test['name'] == 'Dashboard Regulador':
                    stats = result.get('estatisticas', {})
                    print(f"   Em regulação: {stats.get('em_regulacao', 0)}")
                    print(f"   Críticos: {stats.get('criticos', 0)}")
                
                elif test['name'] == 'Processar Regulação IA':
                    analise = result.get('analise_decisoria', {})
                    print(f"   Score: {analise.get('score_prioridade', 'N/A')}/10")
                    print(f"   Risco: {analise.get('classificacao_risco', 'N/A')}")
                    print(f"   Destino: {analise.get('unidade_destino_sugerida', 'N/A')}")
                
            else:
                print(f"❌ {test['name']}: {response.status_code}")
                print(f"   Resposta: {response.text[:100]}...")
                
        except Exception as e:
            print(f"❌ {test['name']}: Erro - {e}")
        
        print()

def main():
    """Função principal"""
    print("=== TESTE DE INTEGRAÇÃO FRONTEND-BACKEND ===\n")
    
    # Verificar se backend está rodando
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code != 200:
            print("❌ Backend não está respondendo corretamente")
            return 1
    except:
        print("❌ Backend não está rodando!")
        print("Execute primeiro: python start_backend_simple.py")
        return 1
    
    print("✅ Backend está rodando\n")
    
    # Testar endpoints básicos
    token = test_backend_endpoints()
    
    # Testar endpoints autenticados
    test_authenticated_endpoints(token)
    
    print("="*50)
    print("🎉 TESTES CONCLUÍDOS!")
    print("="*50)
    
    print("\n📋 Próximos passos:")
    print("1. Se todos os testes passaram, o backend está funcionando")
    print("2. Inicie o frontend: cd regulacao-app && npm start")
    print("3. Teste o login no app com: admin@sesgo.gov.br / admin123")
    print("4. Verifique se os dados aparecem no dashboard")
    
    return 0

if __name__ == "__main__":
    exit(main())