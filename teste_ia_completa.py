#!/usr/bin/env python3
"""Teste da IA completa com BioBERT + Matchmaker"""

import requests
import json

# Dados de teste
dados_paciente = {
    "protocolo": "TEST-IA-COMPLETA-001",
    "especialidade": "CARDIOLOGIA",
    "cid": "I21.0",
    "cid_desc": "Infarto agudo do miocárdio",
    "prontuario_texto": "Paciente masculino, 55 anos, com dor torácica intensa há 2 horas, sudorese profusa, dispneia e náuseas. Dor em aperto, irradiando para braço esquerdo. Histórico de hipertensão arterial.",
    "historico_paciente": "Hipertensão arterial há 10 anos, tabagismo, sedentarismo",
    "prioridade_descricao": "Urgente",
    "cidade_origem": "GOIANIA"
}

print("🤖 TESTE IA COMPLETA - BioBERT + Matchmaker + Pipeline")
print("=" * 60)

try:
    # Chamar a IA
    print("📤 Enviando dados para IA...")
    response = requests.post(
        "http://localhost:8000/processar-regulacao",
        json=dados_paciente,
        timeout=60
    )
    
    if response.status_code == 200:
        resultado = response.json()
        
        print("✅ IA processou com sucesso!")
        print(f"🏥 Hospital: {resultado['analise_decisoria']['unidade_destino_sugerida']}")
        print(f"📊 Score: {resultado['analise_decisoria']['score_prioridade']}/10")
        print(f"🚨 Risco: {resultado['analise_decisoria']['classificacao_risco']}")
        
        # Verificar metadados
        if 'metadata' in resultado:
            metadata = resultado['metadata']
            print(f"⏱️ Tempo: {metadata.get('tempo_processamento', 0):.2f}s")
            print(f"🧬 BioBERT: {'✅' if metadata.get('biobert_usado') else '❌'}")
            print(f"🚑 Matchmaker: {'✅' if metadata.get('matchmaker_usado') else '❌'}")
            
        # Verificar dados logísticos
        if 'matchmaking_logistico' in resultado:
            matchmaking = resultado['matchmaking_logistico']
            print(f"📏 Distância: {matchmaking['distancia_km']} km")
            print(f"⏱️ Tempo transporte: {matchmaking['tempo_estimado_min']} min")
            print(f"🚑 Ambulância: {resultado['ambulancia_sugerida']['id']}")
            
        # Verificar protocolo especial
        if 'protocolo_especial' in resultado and resultado['protocolo_especial'].get('ativo'):
            print(f"⚠️ Protocolo especial: {resultado['protocolo_especial']['tipo']}")
            
        print("\n📋 Justificativa:")
        print(resultado['analise_decisoria']['justificativa_clinica'][:200] + "...")
        
    else:
        print(f"❌ Erro HTTP {response.status_code}: {response.text}")
        
except Exception as e:
    print(f"❌ Erro na requisição: {e}")

print("\n" + "=" * 60)
print("🏁 Teste concluído!")