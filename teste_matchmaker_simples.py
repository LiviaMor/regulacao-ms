#!/usr/bin/env python3
"""Teste simples do Matchmaker"""

import sys
import os
sys.path.append('backend/microservices/shared')

try:
    from matchmaker_logistico import processar_matchmaking
    
    print("🚑 TESTE MATCHMAKER SIMPLES")
    print("=" * 40)
    
    # Dados de teste
    dados_paciente = {
        "protocolo": "TEST-001",
        "cidade_origem": "GOIANIA",
        "especialidade": "CARDIOLOGIA",
        "cid": "I21.0",
        "prontuario_texto": "Dor torácica intensa"
    }
    
    decisao_ia = {
        "analise_decisoria": {
            "unidade_destino_sugerida": "HOSPITAL ESTADUAL DR ALBERTO RASSI HGG",
            "score_prioridade": 8,
            "classificacao_risco": "VERMELHO"
        }
    }
    
    print("Processando matchmaking...")
    resultado = processar_matchmaking(dados_paciente, decisao_ia)
    
    print(f"Hospital: {resultado['matchmaking_logistico']['hospital_destino']}")
    print(f"Distância: {resultado['matchmaking_logistico']['distancia_km']} km")
    print(f"Tempo: {resultado['matchmaking_logistico']['tempo_estimado_min']} min")
    print(f"Ambulância: {resultado['ambulancia_sugerida']['id']}")
    
    print("✅ Matchmaker funcionando!")
        
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()