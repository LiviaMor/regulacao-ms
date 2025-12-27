#!/usr/bin/env python3
"""
Teste do MS-Ingestao - Microserviço de Ingestão e Tendência
Testa a "Memória de Curto Prazo" do sistema de regulação
"""

import requests
import json
from datetime import datetime

# Configuração
BASE_URL = "http://localhost:8004"  # MS-Ingestao direto
# BASE_URL = "http://localhost:8080/ingestao"  # Via API Gateway

def print_header(titulo):
    print(f"\n{'='*60}")
    print(f"  {titulo}")
    print(f"{'='*60}")

def print_resultado(nome, sucesso, detalhes=""):
    status = "✅ PASSOU" if sucesso else "❌ FALHOU"
    print(f"{status} - {nome}")
    if detalhes:
        print(f"   {detalhes}")

def teste_health_check():
    """Testa endpoint de health check"""
    print_header("1. TESTE HEALTH CHECK")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        sucesso = response.status_code == 200
        data = response.json()
        
        print_resultado(
            "Health Check",
            sucesso,
            f"Status: {data.get('status')} | Registros: {data.get('memoria_curto_prazo', {}).get('total_registros', 0)}"
        )
        return sucesso
    except Exception as e:
        print_resultado("Health Check", False, str(e))
        return False

def teste_ingerir_ocupacao():
    """Testa ingestão de dados de ocupação"""
    print_header("2. TESTE INGESTÃO DE OCUPAÇÃO")
    
    dados = {
        "unidade_id": "HGG",
        "unidade_nome": "HOSPITAL ESTADUAL DR ALBERTO RASSI HGG",
        "tipo_leito": "UTI",
        "ocupacao_percentual": 85.5,
        "leitos_totais": 50,
        "leitos_ocupados": 43,
        "leitos_disponiveis": 7,
        "fonte_dados": "TESTE"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/ingerir-ocupacao", json=dados, timeout=5)
        sucesso = response.status_code == 200
        data = response.json()
        
        print_resultado(
            "Ingestão Individual",
            sucesso,
            f"ID: {data.get('id')} | Unidade: {data.get('unidade_id')} | Ocupação: {data.get('ocupacao')}%"
        )
        return sucesso
    except Exception as e:
        print_resultado("Ingestão Individual", False, str(e))
        return False

def teste_ingerir_batch():
    """Testa ingestão em lote"""
    print_header("3. TESTE INGESTÃO EM LOTE")
    
    batch = {
        "registros": [
            {
                "unidade_id": "HUGO",
                "unidade_nome": "HOSPITAL DE URGENCIAS DE GOIAS DR VALDEMIRO CRUZ HUGO",
                "tipo_leito": "TRAUMA",
                "ocupacao_percentual": 92.0,
                "leitos_totais": 80,
                "leitos_ocupados": 74,
                "leitos_disponiveis": 6,
                "fonte_dados": "TESTE"
            },
            {
                "unidade_id": "HEMU",
                "unidade_nome": "HOSPITAL ESTADUAL MATERNO INFANTIL DR JURANDIR DO NASCIMENTO",
                "tipo_leito": "OBSTETRICIA",
                "ocupacao_percentual": 78.0,
                "leitos_totais": 60,
                "leitos_ocupados": 47,
                "leitos_disponiveis": 13,
                "fonte_dados": "TESTE"
            }
        ]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/ingerir-ocupacao-batch", json=batch, timeout=5)
        sucesso = response.status_code == 200
        data = response.json()
        
        print_resultado(
            "Ingestão em Lote",
            sucesso,
            f"Registros: {len(data.get('unidades', []))} | Unidades: {', '.join(data.get('unidades', []))}"
        )
        return sucesso
    except Exception as e:
        print_resultado("Ingestão em Lote", False, str(e))
        return False

def teste_simular_historico():
    """Testa simulação de histórico para cálculo de tendência"""
    print_header("4. TESTE SIMULAÇÃO DE HISTÓRICO")
    
    try:
        response = requests.post(
            f"{BASE_URL}/simular-historico",
            params={
                "unidade_id": "HGG_TESTE",
                "unidade_nome": "Hospital Teste para Tendência",
                "horas": 6
            },
            timeout=10
        )
        sucesso = response.status_code == 200
        data = response.json()
        
        print_resultado(
            "Simulação de Histórico",
            sucesso,
            f"Registros criados: {data.get('registros_criados')} | Período: {data.get('periodo_horas')}h"
        )
        return sucesso
    except Exception as e:
        print_resultado("Simulação de Histórico", False, str(e))
        return False

def teste_tendencia():
    """Testa cálculo de tendência"""
    print_header("5. TESTE CÁLCULO DE TENDÊNCIA")
    
    try:
        response = requests.get(f"{BASE_URL}/tendencia/HGG_TESTE", timeout=5)
        sucesso = response.status_code == 200
        data = response.json()
        
        tendencia = data.get('tendencia', 'N/A')
        variacao = data.get('variacao_6h', 0)
        alerta = data.get('alerta_saturacao', False)
        
        print_resultado(
            "Cálculo de Tendência",
            sucesso,
            f"Tendência: {tendencia} | Variação 6h: {variacao}% | Alerta: {'SIM' if alerta else 'NÃO'}"
        )
        
        if data.get('previsao_saturacao_min'):
            print(f"   ⚠️ Previsão de saturação: {data['previsao_saturacao_min']} minutos")
        
        return sucesso
    except Exception as e:
        print_resultado("Cálculo de Tendência", False, str(e))
        return False

def teste_hospitais_preditivo():
    """Testa endpoint principal para IA - hospitais com tendência"""
    print_header("6. TESTE HOSPITAIS PREDITIVOS (ENDPOINT IA)")
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/inteligencia/hospitais-disponiveis", timeout=10)
        sucesso = response.status_code == 200
        data = response.json()
        
        hospitais = data.get('hospitais', [])
        contexto = data.get('contexto_llm', {})
        
        print_resultado(
            "Hospitais Preditivos",
            sucesso,
            f"Total: {len(hospitais)} | Alertas: {contexto.get('hospitais_com_alerta', 0)} | Alta: {contexto.get('hospitais_tendencia_alta', 0)}"
        )
        
        # Mostrar recomendação para IA
        if contexto.get('recomendacao_ia'):
            print(f"\n   📊 RECOMENDAÇÃO PARA IA:")
            print(f"   {contexto['recomendacao_ia']}")
        
        # Mostrar exemplo de mensagem para IA
        if hospitais:
            print(f"\n   📝 EXEMPLO DE MENSAGEM PARA LLAMA:")
            print(f"   {hospitais[0].get('mensagem_ia', 'N/A')}")
        
        return sucesso
    except Exception as e:
        print_resultado("Hospitais Preditivos", False, str(e))
        return False

def teste_historico():
    """Testa consulta de histórico"""
    print_header("7. TESTE HISTÓRICO DE OCUPAÇÃO")
    
    try:
        response = requests.get(f"{BASE_URL}/historico/HGG_TESTE", params={"horas": 24}, timeout=5)
        sucesso = response.status_code == 200
        data = response.json()
        
        print_resultado(
            "Histórico de Ocupação",
            sucesso,
            f"Registros: {data.get('total_registros')} | Período: {data.get('periodo_horas')}h"
        )
        return sucesso
    except Exception as e:
        print_resultado("Histórico de Ocupação", False, str(e))
        return False

def teste_estatisticas():
    """Testa estatísticas do serviço"""
    print_header("8. TESTE ESTATÍSTICAS")
    
    try:
        response = requests.get(f"{BASE_URL}/estatisticas", timeout=5)
        sucesso = response.status_code == 200
        data = response.json()
        
        stats = data.get('estatisticas', {})
        config = data.get('configuracao', {})
        
        print_resultado(
            "Estatísticas",
            sucesso,
            f"Total: {stats.get('total_registros')} | 24h: {stats.get('registros_ultimas_24h')} | Unidades: {stats.get('unidades_monitoradas')}"
        )
        
        print(f"\n   ⚙️ CONFIGURAÇÃO:")
        print(f"   Janela de tendência: {config.get('janela_tendencia')}")
        print(f"   Limiar ALTA: {config.get('limiar_alta')}")
        print(f"   Limiar QUEDA: {config.get('limiar_queda')}")
        print(f"   Limiar Alerta: {config.get('limiar_alerta_saturacao')}")
        
        return sucesso
    except Exception as e:
        print_resultado("Estatísticas", False, str(e))
        return False

def main():
    print("\n" + "="*60)
    print("  TESTE DO MS-INGESTAO - MEMÓRIA DE CURTO PRAZO")
    print("  Sistema de Regulação SES-GO")
    print("="*60)
    print(f"  URL Base: {BASE_URL}")
    print(f"  Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    resultados = []
    
    # Executar testes
    resultados.append(("Health Check", teste_health_check()))
    resultados.append(("Ingestão Individual", teste_ingerir_ocupacao()))
    resultados.append(("Ingestão em Lote", teste_ingerir_batch()))
    resultados.append(("Simulação Histórico", teste_simular_historico()))
    resultados.append(("Cálculo Tendência", teste_tendencia()))
    resultados.append(("Hospitais Preditivos", teste_hospitais_preditivo()))
    resultados.append(("Histórico", teste_historico()))
    resultados.append(("Estatísticas", teste_estatisticas()))
    
    # Resumo
    print_header("RESUMO DOS TESTES")
    
    passou = sum(1 for _, r in resultados if r)
    total = len(resultados)
    
    for nome, resultado in resultados:
        status = "✅" if resultado else "❌"
        print(f"  {status} {nome}")
    
    print(f"\n  RESULTADO: {passou}/{total} testes passaram")
    
    if passou == total:
        print("\n  🎉 TODOS OS TESTES PASSARAM!")
        print("  O MS-Ingestao está funcionando corretamente.")
    else:
        print(f"\n  ⚠️ {total - passou} teste(s) falharam.")
        print("  Verifique se o serviço está rodando em", BASE_URL)
    
    return passou == total

if __name__ == "__main__":
    main()
