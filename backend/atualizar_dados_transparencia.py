#!/usr/bin/env python3
"""
SCRIPT DE ATUALIZAÇÃO DE DADOS DO PORTAL DA TRANSPARÊNCIA SES-GO
Busca dados atualizados da regulação hospitalar de Goiás
"""

import requests
import json
import os
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# URLs do Portal da Transparência SES-GO (Pentaho)
BASE_URL = "https://indicadores.saude.go.gov.br/pentaho/plugin/cda/api/doQuery"

# Configurações dos endpoints de dados
ENDPOINTS = {
    "em_regulacao": {
        "path": "/public/transparencia_regulacao/regulacao.cda",
        "dataAccessId": "em_regulacao"
    },
    "admitidos": {
        "path": "/public/transparencia_regulacao/regulacao.cda",
        "dataAccessId": "admitidos"
    },
    "em_transito": {
        "path": "/public/transparencia_regulacao/regulacao.cda",
        "dataAccessId": "em_transito"
    },
    "alta": {
        "path": "/public/transparencia_regulacao/regulacao.cda",
        "dataAccessId": "alta"
    },
    "ultima_atualizacao": {
        "path": "/public/transparencia_regulacao/regulacao.cda",
        "dataAccessId": "ultima_atualizacao"
    }
}

def buscar_dados_pentaho(endpoint_config: dict) -> list:
    """
    Busca dados do Pentaho CDA (Community Data Access)
    """
    try:
        params = {
            "path": endpoint_config["path"],
            "dataAccessId": endpoint_config["dataAccessId"],
            "outputType": "json"
        }
        
        response = requests.get(
            BASE_URL,
            params=params,
            timeout=30,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "application/json"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            # Pentaho retorna dados em formato específico
            if "resultset" in data:
                return data["resultset"]
            return data
        else:
            logger.warning(f"Erro ao buscar dados: {response.status_code}")
            return []
            
    except Exception as e:
        logger.error(f"Erro na requisição: {e}")
        return []

def atualizar_arquivos_json():
    """
    Atualiza todos os arquivos JSON com dados do portal
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    arquivos_atualizados = []
    
    for nome, config in ENDPOINTS.items():
        logger.info(f"Buscando dados: {nome}")
        
        dados = buscar_dados_pentaho(config)
        
        if dados:
            arquivo = os.path.join(base_dir, f"dados_{nome}.json")
            
            with open(arquivo, 'w', encoding='utf-8') as f:
                json.dump(dados, f, ensure_ascii=False, indent=4)
            
            arquivos_atualizados.append(nome)
            logger.info(f"✓ {nome}: {len(dados)} registros")
        else:
            logger.warning(f"✗ {nome}: sem dados")
    
    # Atualizar timestamp
    timestamp_file = os.path.join(base_dir, "dados_ultima_atualizacao.json")
    with open(timestamp_file, 'w', encoding='utf-8') as f:
        json.dump([[datetime.now().strftime("%d/%m/%Y %H:%M:%S")]], f)
    
    return arquivos_atualizados

def verificar_conexao_portal():
    """
    Verifica se o portal está acessível
    """
    try:
        response = requests.get(
            "https://indicadores.saude.go.gov.br/pentaho/api/repos/pentaho-cdf-dd/static/logo/logo_normal.png",
            timeout=10
        )
        return response.status_code == 200
    except:
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("ATUALIZAÇÃO DE DADOS - PORTAL TRANSPARÊNCIA SES-GO")
    print("=" * 60)
    
    if verificar_conexao_portal():
        print("✓ Portal acessível")
        atualizados = atualizar_arquivos_json()
        print(f"\nArquivos atualizados: {', '.join(atualizados)}")
    else:
        print("✗ Portal inacessível - usando dados em cache")
