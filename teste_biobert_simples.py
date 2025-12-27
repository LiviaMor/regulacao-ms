#!/usr/bin/env python3
"""Teste simples do BioBERT"""

import sys
import os
sys.path.append('backend/microservices/shared')

try:
    from biobert_service import extrair_entidades_biobert, is_biobert_disponivel
    
    print("🧬 TESTE BIOBERT SIMPLES")
    print("=" * 40)
    
    print(f"BioBERT disponível: {is_biobert_disponivel()}")
    
    if is_biobert_disponivel():
        texto_teste = "Paciente com dor torácica intensa e dispneia"
        print(f"Testando: {texto_teste}")
        
        resultado = extrair_entidades_biobert(texto_teste)
        print(f"Status: {resultado['status']}")
        print(f"Confiança: {resultado.get('confianca', 'N/A')}")
        print(f"Entidades: {len(resultado.get('entidades', []))}")
        
        print("✅ BioBERT funcionando!")
    else:
        print("❌ BioBERT não disponível")
        
except Exception as e:
    print(f"❌ Erro: {e}")