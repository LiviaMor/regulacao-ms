#!/usr/bin/env python3
"""
Script de teste para verificar funcionamento dos microserviços
"""

import requests
import json
import time
from datetime import datetime

def test_microservice(name, url, endpoint="/health"):
    """Testa um microserviço"""
    try:
        response = requests.get(f"{url}{endpoint}", timeout=5)
        if response.status_code == 200:
            print(f"✅ {name}: OK - {response.json().get('status', 'running')}")
            return True
        else:
            print(f"❌ {name}: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ {name}: Erro - {str(e)}")
        return False

def test_ia_integration():
    """Testa integração completa Hospital -> Regulacao"""
    try:
        print("\n🧪 TESTANDO INTEGRAÇÃO COMPLETA...")
        
        # Dados de teste
        paciente_teste = {
            "protocolo": f"TEST-{int(time.time())}",
            "especialidade": "ORTOPEDIA",
            "cid": "M54.5",
            "cid_desc": "Dor lombar",
            "prontuario_texto": "Paciente com dor lombar crônica, sem sinais de trauma",
            "historico_paciente": "Histórico de dor lombar há 6 meses",
            "prioridade_descricao": "Normal"
        }
        
        # Teste 1: MS-Regulacao (IA direta)
        print("🧠 Testando MS-Regulacao (IA)...")
        response = requests.post(
            "http://localhost:8002/processar-regulacao",
            json=paciente_teste,
            timeout=30
        )
        
        if response.status_code == 200:
            resultado_ia = response.json()
            print(f"✅ IA processou: {resultado_ia['analise_decisoria']['classificacao_risco']} - Score {resultado_ia['analise_decisoria']['score_prioridade']}/10")
            print(f"🏥 Hospital sugerido: {resultado_ia['analise_decisoria']['unidade_destino_sugerida']}")
            
            # Verificar se não foi para o HUGO (dor lombar não deve ir para trauma)
            hospital_sugerido = resultado_ia['analise_decisoria']['unidade_destino_sugerida']
            if "HUGO" not in hospital_sugerido:
                print("✅ Pipeline funcionando: Dor lombar NÃO foi para HUGO (correto)")
            else:
                print("⚠️ Pipeline pode ter problema: Dor lombar foi para HUGO")
            
            return True
        else:
            print(f"❌ Erro na IA: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste de integração: {str(e)}")
        return False

def test_api_gateway():
    """Testa API Gateway"""
    try:
        print("\n🌐 TESTANDO API GATEWAY...")
        
        # Teste de roteamento
        endpoints_teste = [
            ("/health", "Gateway Health"),
            ("/hospital/health", "MS-Hospital via Gateway"),
            ("/regulacao/health", "MS-Regulacao via Gateway"),
            ("/transferencia/health", "MS-Transferencia via Gateway")
        ]
        
        gateway_ok = True
        for endpoint, desc in endpoints_teste:
            try:
                response = requests.get(f"http://localhost:8080{endpoint}", timeout=5)
                if response.status_code == 200:
                    print(f"✅ {desc}: OK")
                else:
                    print(f"❌ {desc}: HTTP {response.status_code}")
                    gateway_ok = False
            except Exception as e:
                print(f"❌ {desc}: {str(e)}")
                gateway_ok = False
        
        return gateway_ok
        
    except Exception as e:
        print(f"❌ Erro no teste do Gateway: {str(e)}")
        return False

def main():
    print("🧪 TESTE DE MICROSERVIÇOS - SISTEMA DE REGULAÇÃO SES-GO")
    print("=" * 60)
    print(f"⏰ Iniciado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Testes individuais
    print("📊 TESTANDO MICROSERVIÇOS INDIVIDUAIS...")
    ms_hospital = test_microservice("MS-Hospital", "http://localhost:8001")
    ms_regulacao = test_microservice("MS-Regulacao", "http://localhost:8002")
    ms_transferencia = test_microservice("MS-Transferencia", "http://localhost:8003")
    
    # Teste do Gateway
    gateway_ok = test_api_gateway()
    
    # Teste de integração
    if ms_regulacao:
        ia_ok = test_ia_integration()
    else:
        ia_ok = False
        print("⚠️ Pulando teste de IA (MS-Regulacao não disponível)")
    
    # Resumo
    print("\n" + "=" * 60)
    print("📋 RESUMO DOS TESTES:")
    print(f"🏥 MS-Hospital:      {'✅ OK' if ms_hospital else '❌ FALHOU'}")
    print(f"🧠 MS-Regulacao:     {'✅ OK' if ms_regulacao else '❌ FALHOU'}")
    print(f"🚑 MS-Transferencia: {'✅ OK' if ms_transferencia else '❌ FALHOU'}")
    print(f"🌐 API Gateway:      {'✅ OK' if gateway_ok else '❌ FALHOU'}")
    print(f"🤖 IA Integração:    {'✅ OK' if ia_ok else '❌ FALHOU'}")
    
    total_testes = 5
    testes_ok = sum([ms_hospital, ms_regulacao, ms_transferencia, gateway_ok, ia_ok])
    
    print(f"\n🎯 RESULTADO: {testes_ok}/{total_testes} testes passaram")
    
    if testes_ok == total_testes:
        print("🎉 TODOS OS MICROSERVIÇOS FUNCIONANDO PERFEITAMENTE!")
    elif testes_ok >= 3:
        print("⚠️ Maioria dos serviços funcionando, verificar falhas")
    else:
        print("❌ Problemas críticos detectados")
    
    print("\n💡 DICAS:")
    print("- Certifique-se que o Docker está rodando")
    print("- Execute: docker-compose -f docker-compose.microservices.yml up -d")
    print("- Aguarde alguns segundos para inicialização completa")
    print("=" * 60)

if __name__ == "__main__":
    main()