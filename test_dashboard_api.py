#!/usr/bin/env python3
"""
Script para testar a API do dashboard com dados reais
"""

import requests
import json
import time

def test_dashboard_api():
    """Testa a API do dashboard"""
    
    base_url = "http://localhost:8000"
    
    print("=== TESTE DA API DO DASHBOARD ===\n")
    
    # 1. Testar health check
    print("1. Testando health check...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            print("   ✓ API está funcionando")
        else:
            print(f"   ✗ Erro no health check: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ✗ Erro ao conectar com a API: {e}")
        return False
    
    # 2. Testar carregamento de dados JSON
    print("\n2. Carregando dados JSON...")
    try:
        response = requests.post(f"{base_url}/load-json-data", timeout=60)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Dados carregados: {data.get('total_registros', 0)} registros")
        else:
            print(f"   ⚠ Aviso no carregamento: {response.status_code}")
            print(f"     Resposta: {response.text}")
    except Exception as e:
        print(f"   ⚠ Erro no carregamento (continuando): {e}")
    
    # 3. Testar endpoint do dashboard
    print("\n3. Testando endpoint do dashboard...")
    try:
        response = requests.get(f"{base_url}/dashboard/leitos", timeout=30)
        if response.status_code == 200:
            data = response.json()
            
            print(f"   ✓ Dashboard funcionando")
            print(f"   ✓ Fonte dos dados: {data.get('fonte', 'N/A')}")
            print(f"   ✓ Última atualização: {data.get('ultima_atualizacao', 'N/A')}")
            
            # Status summary
            status_summary = data.get('status_summary', [])
            if status_summary:
                print(f"\n   📊 Resumo por Status:")
                for status in status_summary:
                    print(f"      - {status['status']}: {status['count']} pacientes")
            
            # Unidades com pressão
            unidades_pressao = data.get('unidades_pressao', [])
            if unidades_pressao:
                print(f"\n   🏥 Top 5 Unidades com Maior Pressão:")
                for i, unidade in enumerate(unidades_pressao[:5], 1):
                    print(f"      {i}. {unidade['unidade_executante_desc']}")
                    print(f"         📍 {unidade['cidade']} - {unidade['pacientes_em_fila']} pacientes")
            
            # Especialidades (se disponível)
            especialidades = data.get('especialidades_demanda', [])
            if especialidades:
                print(f"\n   🩺 Top 5 Especialidades:")
                for i, esp in enumerate(especialidades[:5], 1):
                    print(f"      {i}. {esp['especialidade']}: {esp['count']} solicitações")
            
            # Salvar dados para inspeção
            with open('dashboard_api_response.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
            print(f"\n   ✓ Resposta salva em: dashboard_api_response.json")
            
            return True
            
        else:
            print(f"   ✗ Erro no dashboard: {response.status_code}")
            print(f"     Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ✗ Erro ao testar dashboard: {e}")
        return False

def test_other_endpoints():
    """Testa outros endpoints da API"""
    
    base_url = "http://localhost:8000"
    
    print("\n4. Testando outros endpoints...")
    
    # Testar endpoint de pacientes
    try:
        response = requests.get(f"{base_url}/pacientes?limit=5", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Endpoint pacientes: {len(data)} registros retornados")
        else:
            print(f"   ⚠ Endpoint pacientes: {response.status_code}")
    except Exception as e:
        print(f"   ⚠ Erro no endpoint pacientes: {e}")
    
    # Testar endpoint raiz
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Endpoint raiz: {data.get('service', 'N/A')}")
        else:
            print(f"   ⚠ Endpoint raiz: {response.status_code}")
    except Exception as e:
        print(f"   ⚠ Erro no endpoint raiz: {e}")

def main():
    """Função principal"""
    
    print("Aguardando 3 segundos para garantir que a API esteja pronta...")
    time.sleep(3)
    
    success = test_dashboard_api()
    
    if success:
        test_other_endpoints()
        print("\n=== TESTE CONCLUÍDO COM SUCESSO ===")
        print("\nPróximos passos:")
        print("1. Acesse http://localhost:8000/docs para ver a documentação da API")
        print("2. Teste o dashboard no app React Native")
        print("3. Verifique os dados em dashboard_api_response.json")
        return 0
    else:
        print("\n=== TESTE FALHOU ===")
        print("\nVerifique se:")
        print("1. A API está rodando em http://localhost:8000")
        print("2. Os arquivos JSON estão no diretório correto")
        print("3. As dependências estão instaladas (pandas, requests)")
        return 1

if __name__ == "__main__":
    exit(main())