#!/usr/bin/env python3
"""
Script para iniciar todos os serviços do sistema de regulação
Inicia: Backend Principal (8000) + MS-Ingestao (8004)
E faz a sincronização inicial automaticamente
"""

import subprocess
import time
import requests
import sys
import os
import signal
from threading import Thread

# Cores para output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_status(msg, color=Colors.GREEN):
    print(f"{color}[SISTEMA] {msg}{Colors.END}")

def check_service(url, name, timeout=5):
    """Verifica se um serviço está respondendo"""
    try:
        response = requests.get(url, timeout=timeout)
        return response.status_code == 200
    except:
        return False

def wait_for_service(url, name, max_attempts=30):
    """Aguarda um serviço ficar disponível"""
    print_status(f"Aguardando {name} iniciar...", Colors.YELLOW)
    for i in range(max_attempts):
        if check_service(url, name):
            print_status(f"✅ {name} está rodando!", Colors.GREEN)
            return True
        time.sleep(1)
        if i % 5 == 0:
            print_status(f"   Tentativa {i+1}/{max_attempts}...", Colors.YELLOW)
    print_status(f"❌ {name} não iniciou após {max_attempts} segundos", Colors.RED)
    return False

def sincronizar_ocupacao():
    """Sincroniza dados de ocupação com MS-Ingestao"""
    try:
        print_status("Sincronizando dados de ocupação...", Colors.BLUE)
        response = requests.post("http://localhost:8000/sincronizar-ocupacao", timeout=30)
        if response.status_code == 200:
            data = response.json()
            print_status(f"✅ Sincronização: {data.get('message', 'OK')}", Colors.GREEN)
            return True
        else:
            print_status(f"⚠️ Sincronização retornou status {response.status_code}", Colors.YELLOW)
            return False
    except Exception as e:
        print_status(f"❌ Erro na sincronização: {e}", Colors.RED)
        return False

def main():
    print_status("=" * 60, Colors.BLUE)
    print_status("SISTEMA DE REGULAÇÃO SES-GO - INICIALIZAÇÃO", Colors.BLUE)
    print_status("=" * 60, Colors.BLUE)
    
    processes = []
    
    try:
        # Diretório base
        base_dir = os.path.dirname(os.path.abspath(__file__))
        ms_ingestao_dir = os.path.join(base_dir, "microservices", "ms-ingestao")
        
        # 1. Iniciar MS-Ingestao (porta 8004)
        print_status("Iniciando MS-Ingestao (porta 8004)...", Colors.YELLOW)
        ms_ingestao_process = subprocess.Popen(
            [sys.executable, "main.py"],
            cwd=ms_ingestao_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        processes.append(("MS-Ingestao", ms_ingestao_process))
        
        # Aguardar MS-Ingestao
        if not wait_for_service("http://localhost:8004/health", "MS-Ingestao", max_attempts=20):
            print_status("Continuando sem MS-Ingestao...", Colors.YELLOW)
        
        # 2. Iniciar Backend Principal (porta 8000)
        print_status("Iniciando Backend Principal (porta 8000)...", Colors.YELLOW)
        backend_process = subprocess.Popen(
            [sys.executable, "main_unified.py"],
            cwd=base_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        processes.append(("Backend", backend_process))
        
        # Aguardar Backend
        if not wait_for_service("http://localhost:8000/health", "Backend Principal", max_attempts=30):
            print_status("❌ Backend não iniciou corretamente", Colors.RED)
            raise Exception("Backend falhou ao iniciar")
        
        # 3. Sincronizar dados
        time.sleep(2)  # Pequena pausa para estabilizar
        sincronizar_ocupacao()
        
        # Status final
        print_status("=" * 60, Colors.GREEN)
        print_status("✅ SISTEMA INICIADO COM SUCESSO!", Colors.GREEN)
        print_status("=" * 60, Colors.GREEN)
        print_status("Serviços ativos:", Colors.BLUE)
        print_status("  • Backend Principal: http://localhost:8000", Colors.GREEN)
        print_status("  • MS-Ingestao:       http://localhost:8004", Colors.GREEN)
        print_status("  • Docs API:          http://localhost:8000/docs", Colors.GREEN)
        print_status("=" * 60, Colors.GREEN)
        print_status("Pressione Ctrl+C para encerrar todos os serviços", Colors.YELLOW)
        
        # Manter rodando e mostrar logs
        while True:
            for name, proc in processes:
                if proc.poll() is not None:
                    print_status(f"⚠️ {name} encerrou inesperadamente", Colors.RED)
            time.sleep(5)
            
    except KeyboardInterrupt:
        print_status("\nEncerrando serviços...", Colors.YELLOW)
    finally:
        for name, proc in processes:
            if proc.poll() is None:
                print_status(f"Encerrando {name}...", Colors.YELLOW)
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except:
                    proc.kill()
        print_status("Todos os serviços encerrados.", Colors.GREEN)

if __name__ == "__main__":
    main()
