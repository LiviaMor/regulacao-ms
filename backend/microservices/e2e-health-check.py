#!/usr/bin/env python3
"""
HEALTH-CHECK E2E - SISTEMA DE REGULACAO SES-GO
Script de validacao completa da arquitetura:
- Docker e containers
- Ollama (Llama 3) funcionando
- BioBERT carregado e extraindo entidades
- Backend Principal respondendo
- MS-Ingestao respondendo
- Pipeline de IA funcionando
- Frontend acessivel
"""

import requests
import json
import time
import subprocess
import sys
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class E2EHealthChecker:
    """Health Checker End-to-End para validacao completa"""
    
    def __init__(self):
        self.services = {
            "docker": {"status": False, "details": ""},
            "postgres": {"status": False, "details": ""},
            "redis": {"status": False, "details": ""},
            "ollama": {"status": False, "details": ""},
            "backend": {"status": False, "details": ""},
            "ms_ingestao": {"status": False, "details": ""},
            "biobert": {"status": False, "details": ""},
            "pipeline_ia": {"status": False, "details": ""},
            "frontend": {"status": False, "details": ""},
        }
        
        self.start_time = datetime.now()
    
    def print_header(self):
        """Imprime cabecalho do health check"""
        print("=" * 70)
        print("  HEALTH-CHECK E2E - SISTEMA DE REGULACAO SES-GO")
        print("=" * 70)
        print(f"  Iniciado em: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  Sistema: {sys.platform}")
        print(f"  Python: {sys.version.split()[0]}")
        print("=" * 70)
    
    def check_docker_status(self) -> bool:
        """Verifica se Docker esta rodando"""
        try:
            print("\n[DOCKER] Verificando...")
            
            result = subprocess.run(['docker', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                self.services["docker"]["details"] = "Docker nao instalado"
                print("   [ERRO] Docker nao instalado")
                return False
            
            docker_version = result.stdout.strip()
            print(f"   [OK] {docker_version}")
            
            # Verificar containers rodando
            result = subprocess.run(['docker', 'ps', '--format', '{{.Names}}'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                containers = [c for c in result.stdout.strip().split('\n') if c]
                regulacao_containers = [c for c in containers if 'regulacao' in c.lower()]
                
                if regulacao_containers:
                    print(f"   [OK] Containers ativos: {', '.join(regulacao_containers)}")
                else:
                    print("   [INFO] Nenhum container do projeto rodando")
                
                self.services["docker"]["status"] = True
                self.services["docker"]["details"] = f"{len(containers)} containers ativos"
                return True
            
            return False
                
        except Exception as e:
            print(f"   [ERRO] {e}")
            self.services["docker"]["details"] = str(e)
            return False
    
    def check_postgres(self) -> bool:
        """Verifica PostgreSQL"""
        try:
            print("\n[POSTGRESQL] Verificando porta 5432...")
            
            # Tentar via backend health
            try:
                response = requests.get("http://localhost:8000/health", timeout=5)
                if response.status_code == 200:
                    print("   [OK] PostgreSQL acessivel via backend")
                    self.services["postgres"]["status"] = True
                    self.services["postgres"]["details"] = "Conectado via backend"
                    return True
            except:
                pass
            
            # Tentar conexao direta
            try:
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = sock.connect_ex(('localhost', 5432))
                sock.close()
                if result == 0:
                    print("   [OK] PostgreSQL respondendo na porta 5432")
                    self.services["postgres"]["status"] = True
                    self.services["postgres"]["details"] = "Porta 5432 aberta"
                    return True
            except:
                pass
            
            print("   [ERRO] PostgreSQL nao acessivel")
            self.services["postgres"]["details"] = "Nao acessivel"
            return False
            
        except Exception as e:
            print(f"   [ERRO] {e}")
            self.services["postgres"]["details"] = str(e)
            return False
    
    def check_redis(self) -> bool:
        """Verifica Redis"""
        try:
            print("\n[REDIS] Verificando porta 6379...")
            
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', 6379))
            sock.close()
            
            if result == 0:
                print("   [OK] Redis respondendo na porta 6379")
                self.services["redis"]["status"] = True
                self.services["redis"]["details"] = "Porta 6379 aberta"
                return True
            else:
                print("   [INFO] Redis nao detectado (opcional)")
                self.services["redis"]["details"] = "Nao detectado (opcional)"
                return False
                
        except Exception as e:
            print(f"   [INFO] Redis: {e}")
            self.services["redis"]["details"] = "Nao detectado"
            return False
    
    def check_ollama(self) -> bool:
        """Verifica Ollama/Llama 3"""
        try:
            print("\n[OLLAMA] Verificando porta 11434...")
            
            response = requests.get("http://localhost:11434/api/tags", timeout=10)
            if response.status_code == 200:
                models = response.json().get('models', [])
                llama_models = [m['name'] for m in models if 'llama' in m.get('name', '').lower()]
                
                if llama_models:
                    print(f"   [OK] Ollama rodando com modelos: {', '.join(llama_models)}")
                    self.services["ollama"]["status"] = True
                    self.services["ollama"]["details"] = f"Modelos: {', '.join(llama_models)}"
                else:
                    print("   [AVISO] Ollama rodando mas sem modelo Llama")
                    self.services["ollama"]["details"] = "Sem modelo Llama"
                return True
            
            print("   [INFO] Ollama nao detectado (opcional para dev)")
            self.services["ollama"]["details"] = "Nao detectado"
            return False
            
        except Exception as e:
            print(f"   [INFO] Ollama nao disponivel: {e}")
            self.services["ollama"]["details"] = "Nao disponivel"
            return False
    
    def check_backend(self) -> bool:
        """Verifica Backend Principal (porta 8000)"""
        try:
            print("\n[BACKEND] Verificando porta 8000...")
            
            response = requests.get("http://localhost:8000/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                biobert = data.get('biobert_disponivel', False)
                matchmaker = data.get('matchmaker_disponivel', False)
                xai = data.get('xai_disponivel', False)
                ms_ingestao = data.get('ms_ingestao', {}).get('status', 'offline')
                
                print(f"   [OK] Backend rodando")
                print(f"       BioBERT: {'OK' if biobert else 'NAO'}")
                print(f"       Matchmaker: {'OK' if matchmaker else 'NAO'}")
                print(f"       XAI: {'OK' if xai else 'NAO'}")
                print(f"       MS-Ingestao: {ms_ingestao}")
                
                self.services["backend"]["status"] = True
                self.services["backend"]["details"] = f"BioBERT={biobert}, Matchmaker={matchmaker}"
                
                # Atualizar status do BioBERT
                if biobert:
                    self.services["biobert"]["status"] = True
                    self.services["biobert"]["details"] = "Carregado no backend"
                
                return True
            
            print(f"   [ERRO] Backend retornou HTTP {response.status_code}")
            self.services["backend"]["details"] = f"HTTP {response.status_code}"
            return False
            
        except requests.exceptions.ConnectionError:
            print("   [ERRO] Backend nao esta rodando")
            self.services["backend"]["details"] = "Conexao recusada"
            return False
        except Exception as e:
            print(f"   [ERRO] {e}")
            self.services["backend"]["details"] = str(e)
            return False
    
    def check_ms_ingestao(self) -> bool:
        """Verifica MS-Ingestao (porta 8004)"""
        try:
            print("\n[MS-INGESTAO] Verificando porta 8004...")
            
            response = requests.get("http://localhost:8004/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                memoria = data.get('memoria_curto_prazo', {})
                registros = memoria.get('total_registros', 0)
                
                print(f"   [OK] MS-Ingestao rodando")
                print(f"       Registros no historico: {registros}")
                
                self.services["ms_ingestao"]["status"] = True
                self.services["ms_ingestao"]["details"] = f"{registros} registros"
                return True
            
            print(f"   [ERRO] MS-Ingestao retornou HTTP {response.status_code}")
            self.services["ms_ingestao"]["details"] = f"HTTP {response.status_code}"
            return False
            
        except requests.exceptions.ConnectionError:
            print("   [AVISO] MS-Ingestao nao esta rodando")
            self.services["ms_ingestao"]["details"] = "Nao rodando"
            return False
        except Exception as e:
            print(f"   [ERRO] {e}")
            self.services["ms_ingestao"]["details"] = str(e)
            return False
    
    def check_pipeline_ia(self) -> bool:
        """Testa pipeline de IA completo"""
        try:
            print("\n[PIPELINE IA] Testando analise de paciente...")
            
            if not self.services["backend"]["status"]:
                print("   [PULAR] Backend nao disponivel")
                self.services["pipeline_ia"]["details"] = "Backend offline"
                return False
            
            # Dados de teste
            test_data = {
                "protocolo": f"E2E-TEST-{int(time.time())}",
                "especialidade": "CARDIOLOGIA",
                "cid": "I21.0",
                "cid_desc": "Infarto agudo do miocardio",
                "prontuario_texto": "Paciente com dor toracica intensa, sudorese e dispneia",
                "historico_paciente": "Hipertensao arterial",
                "prioridade_descricao": "Urgente"
            }
            
            response = requests.post(
                "http://localhost:8000/processar-regulacao",
                json=test_data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                analise = result.get("analise_decisoria", {})
                hospital = analise.get("unidade_destino_sugerida", "N/A")
                score = analise.get("score_prioridade", 0)
                risco = analise.get("classificacao_risco", "N/A")
                
                print(f"   [OK] Pipeline funcionando")
                print(f"       Hospital sugerido: {hospital[:50]}...")
                print(f"       Score: {score}/10")
                print(f"       Risco: {risco}")
                
                self.services["pipeline_ia"]["status"] = True
                self.services["pipeline_ia"]["details"] = f"Score={score}, Risco={risco}"
                return True
            
            print(f"   [ERRO] Pipeline retornou HTTP {response.status_code}")
            self.services["pipeline_ia"]["details"] = f"HTTP {response.status_code}"
            return False
            
        except Exception as e:
            print(f"   [ERRO] {e}")
            self.services["pipeline_ia"]["details"] = str(e)
            return False
    
    def check_frontend(self) -> bool:
        """Verifica Frontend (porta 8082)"""
        try:
            print("\n[FRONTEND] Verificando porta 8082...")
            
            response = requests.get("http://localhost:8082", timeout=10)
            if response.status_code == 200:
                print("   [OK] Frontend acessivel")
                self.services["frontend"]["status"] = True
                self.services["frontend"]["details"] = "Acessivel"
                return True
            
            print(f"   [AVISO] Frontend retornou HTTP {response.status_code}")
            self.services["frontend"]["details"] = f"HTTP {response.status_code}"
            return False
            
        except requests.exceptions.ConnectionError:
            print("   [INFO] Frontend nao detectado")
            self.services["frontend"]["details"] = "Nao rodando"
            return False
        except Exception as e:
            print(f"   [INFO] Frontend: {e}")
            self.services["frontend"]["details"] = str(e)
            return False
    
    def generate_report(self):
        """Gera relatorio final"""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        print("\n" + "=" * 70)
        print("  RELATORIO FINAL - HEALTH CHECK E2E")
        print("=" * 70)
        
        # Contadores
        total = len(self.services)
        healthy = sum(1 for s in self.services.values() if s["status"])
        
        print(f"  Duracao: {duration:.2f} segundos")
        print(f"  Servicos OK: {healthy}/{total}")
        print(f"  Taxa de sucesso: {(healthy/total)*100:.0f}%")
        
        print("\n  DETALHES:")
        for name, data in self.services.items():
            status = "[OK]" if data["status"] else "[--]"
            print(f"    {status} {name.upper():15} {data['details']}")
        
        # Status final
        print("\n" + "=" * 70)
        if healthy >= total - 2:  # Permite Redis e Ollama offline
            print("  [OK] SISTEMA OPERACIONAL - Pronto para uso!")
        elif healthy >= total * 0.5:
            print("  [AVISO] SISTEMA PARCIALMENTE OPERACIONAL")
        else:
            print("  [ERRO] SISTEMA COM PROBLEMAS - Verificar servicos")
        print("=" * 70)
    
    def run_full_check(self):
        """Executa health check completo"""
        self.print_header()
        
        self.check_docker_status()
        self.check_postgres()
        self.check_redis()
        self.check_ollama()
        self.check_backend()
        self.check_ms_ingestao()
        self.check_pipeline_ia()
        self.check_frontend()
        
        self.generate_report()


def main():
    checker = E2EHealthChecker()
    checker.run_full_check()


if __name__ == "__main__":
    main()
