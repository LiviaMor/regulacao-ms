#!/usr/bin/env python3
"""
Script de teste para o processador de dados SES-GO
"""

import sys
import os
from pathlib import Path

# Adicionar o diretório backend ao path
backend_dir = Path(__file__).parent / "backend"
sys.path.append(str(backend_dir))

from data_processor import SESGoDataProcessor
import json

def main():
    print("=== TESTE DO PROCESSADOR DE DADOS SES-GO ===\n")
    
    # Inicializar processador
    processor = SESGoDataProcessor(".")
    
    print("1. Verificando arquivos de dados...")
    for status, filename in processor.data_files.items():
        file_path = Path(filename)
        exists = "✓" if file_path.exists() else "✗"
        print(f"   {exists} {filename}")
    
    print("\n2. Processando dados...")
    try:
        dashboard_data = processor.generate_dashboard_data()
        
        print(f"   ✓ Total de registros: {dashboard_data.get('total_registros', 0)}")
        print(f"   ✓ Qualidade dos dados: {dashboard_data.get('data_quality', {}).get('score', 0)}/100")
        
        # Status summary
        print("\n3. Resumo por Status:")
        for status in dashboard_data.get('status_summary', []):
            print(f"   - {status['status']}: {status['count']} pacientes")
        
        # Unidades com pressão
        print("\n4. Top 5 Unidades com Maior Pressão:")
        for i, unidade in enumerate(dashboard_data.get('unidades_pressao', [])[:5], 1):
            print(f"   {i}. {unidade['unidade_executante_desc']}")
            print(f"      📍 {unidade['cidade']} - {unidade['pacientes_em_fila']} pacientes")
        
        # Especialidades
        print("\n5. Top 5 Especialidades em Demanda:")
        for i, esp in enumerate(dashboard_data.get('especialidades_demanda', [])[:5], 1):
            print(f"   {i}. {esp['especialidade']}: {esp['count']} solicitações")
        
        # Métricas de tempo
        metricas = dashboard_data.get('metricas_tempo', {})
        if metricas:
            print("\n6. Métricas Temporais:")
            print(f"   - Últimas 24h: {metricas.get('solicitacoes_24h', 0)} solicitações")
            print(f"   - Últimos 7 dias: {metricas.get('solicitacoes_7d', 0)} solicitações")
            print(f"   - Últimos 30 dias: {metricas.get('solicitacoes_30d', 0)} solicitações")
            print(f"   - Tendência: {metricas.get('tendencia', 'N/A')}")
        
        # Qualidade dos dados
        quality = dashboard_data.get('data_quality', {})
        print(f"\n7. Qualidade dos Dados: {quality.get('score', 0)}/100")
        if quality.get('issues'):
            print("   Problemas identificados:")
            for issue in quality['issues']:
                print(f"   - {issue}")
        
        print(f"\n8. Última atualização: {dashboard_data.get('ultima_atualizacao')}")
        
        # Salvar dados processados para inspeção
        output_file = "dashboard_data_test.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(dashboard_data, f, ensure_ascii=False, indent=2, default=str)
        print(f"\n✓ Dados salvos em: {output_file}")
        
        # Exportar dados processados
        print("\n9. Exportando dados processados...")
        processor.export_processed_data("test_processed_data")
        print("   ✓ Dados exportados para: test_processed_data/")
        
        print("\n=== TESTE CONCLUÍDO COM SUCESSO ===")
        
    except Exception as e:
        print(f"\n✗ Erro durante o processamento: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())