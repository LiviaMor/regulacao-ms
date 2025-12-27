"""
Utilitários compartilhados entre microserviços
"""

import logging
import requests
from datetime import datetime
from typing import Dict, Any, Optional
import json

logger = logging.getLogger(__name__)

class MicroserviceClient:
    """Cliente para comunicação entre microserviços"""
    
    def __init__(self, base_url: str, service_name: str):
        self.base_url = base_url
        self.service_name = service_name
    
    def get(self, endpoint: str, params: Dict = None, headers: Dict = None) -> Dict:
        """Requisição GET para outro microserviço"""
        try:
            url = f"{self.base_url}{endpoint}"
            response = requests.get(url, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Erro na comunicação com {self.service_name}: {e}")
            raise
    
    def post(self, endpoint: str, data: Dict = None, headers: Dict = None) -> Dict:
        """Requisição POST para outro microserviço"""
        try:
            url = f"{self.base_url}{endpoint}"
            response = requests.post(url, json=data, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Erro na comunicação com {self.service_name}: {e}")
            raise

def setup_logging(service_name: str):
    """Configurar logging para microserviço"""
    logging.basicConfig(
        level=logging.INFO,
        format=f'%(asctime)s - {service_name} - %(levelname)s - %(message)s'
    )
    return logging.getLogger(service_name)

def create_audit_log(protocolo: str, action: str, user_email: str, 
                    data: Dict[str, Any], microservice: str) -> Dict:
    """Criar log de auditoria padronizado"""
    return {
        "protocolo": protocolo,
        "action": action,
        "user_email": user_email,
        "microservice": microservice,
        "timestamp": datetime.utcnow().isoformat(),
        "data": data
    }

def validate_protocolo(protocolo: str) -> bool:
    """Validar formato do protocolo"""
    if not protocolo or len(protocolo) < 3:
        return False
    return True

def mask_cpf(cpf: str) -> str:
    """Mascarar CPF para LGPD"""
    if not cpf or len(cpf) != 11:
        return "***.***.***-**"
    return f"{cpf[:3]}.***.***-{cpf[-2:]}"

def format_datetime(dt: datetime) -> str:
    """Formatar datetime para ISO string"""
    if dt:
        return dt.isoformat()
    return None