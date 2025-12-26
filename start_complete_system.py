#!/usr/bin/env python3
"""
Script completo para iniciar o Sistema de Regulação SES-GO
com PostgreSQL e dados reais
"""

import subprocess
import sys
import time
import requests
import os
from pathlib import Path

def add_postgresql_to_path():
    """Adiciona PostgreSQL ao PATH da sessão"""
    postgres_paths = [
        r"C:\Program Files\PostgreSQL\15\bin",
        r"C:\Program Files\PostgreSQL\14\bin",
        r"C:\Program Files\PostgreSQL\13\bin"
    ]
    
    for path in postgres_paths:
        if os.path.exists(path):
            current_path = os.environ.get('PATH', '')
            if path not in current_path:
                os.environ['PATH'] = f"{path};{current_path}"
                print(f"✅ PostgreSQL adicionado ao PATH: {path}")
                return True
    
    print("⚠️ PostgreSQL não encontrado nos caminhos padrão")
    return False

def check_postgresql():
    """Verifica se PostgreSQL está funcionando"""
    try:
        result = subprocess.run(['psql', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ PostgreSQL: {result.stdout.strip()}")
            return True
        else:
            return False
    except FileNotFoundError:
        return False

def test_database_connection():
    """Testa conexão com o banco de dados"""
    try:
        import psycopg2
        conn = psycopg2.connect(
            host='localhost',
            port=5432,
            user='regulacao_user',
            password='regulacao_pass',
            database='regulacao_db'
        )
        conn.close()
        print("✅ Conexão com banco de dados OK")
        return True
    except Exception as e:
        print(f"❌ Erro na conexão com banco: {e}")
        return False

def start_backend():
    """Inicia o backend"""
    try:
        print("🚀 Iniciando backend...")
        process = subprocess.Popen([
            sys.executable, "backend/main_unified.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Aguardar inicialização
        time.sleep(8)
        
        # Testar se está funcionando
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ Backend iniciado com sucesso")
                return process
            else:
                print("❌ Backend não está respondendo")
                process.terminate()
                return None
        except:
            print("❌ Não foi possível conectar ao backend")
            process.terminate()
            return None
            
    except Exception as e:
        print(f"❌ Erro ao iniciar backend: {e}")
        return None

def load_data():
    """Carrega dados JSON na API"""
    try:
        print("📊 Carregando dados...")
        response = requests.post("http://localhost:8000/load-json-data", timeout=60)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Dados carregados: {data.get('total_registros', 0)} registros")
            return True
        else:
            print(f"⚠️ Aviso no carregamento: {response.status_code}")
            return True
    except Exception as e:
        print(f"⚠️ Erro no carregamento: {e}")
        return True

def test_dashboard():
    """Testa o dashboard"""
    try:
        print("🧪 Testando dashboard...")
        response = requests.get("http://localhost:8000/dashboard/leitos", timeout=10)
        if response.status_code == 200:
            data = response.json()
            
            total_registros = 0
            for status in data.get('status_summary', []):
                total_registros += status.get('count', 0)
            
            print(f"✅ Dashboard OK: {total_registros} registros")
            
            # Mostrar estatísticas principais
            unidades = data.get('unidades_pressao', [])
            if unidades:
                print(f"   🏥 {len(unidades)} unidades monitoradas")
                top_unidade = unidades[0]
                print(f"   📈 Maior pressão: {top_unidade['unidade_executante_desc']}")
                print(f"      📍 {top_unidade['cidade']} - {top_unidade['pacientes_em_fila']} pacientes")
            
            especialidades = data.get('especialidades_demanda', [])
            if especialidades:
                top_esp = especialidades[0]
                print(f"   🩺 Maior demanda: {top_esp['especialidade']} ({top_esp['count']} solicitações)")
            
            return True
        else:
            print(f"❌ Dashboard com erro: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao testar dashboard: {e}")
        return False

def show_system_info():
    """Mostra informações do sistema"""
    print("\n" + "="*60)
    print("🎉 SISTEMA DE REGULAÇÃO SES-GO INICIADO COM SUCESSO!")
    print("="*60)
    
    print("\n📋 Informações do Sistema:")
    print("   • Backend API: http://localhost:8000")
    print("   • Documentação: http://localhost:8000/docs")
    print("   • Dashboard: http://localhost:8000/dashboard/leitos")
    print("   • Health Check: http://localhost:8000/health")
    print("   • Estatísticas: http://localhost:8000/stats")
    
    print("\n🗄️ Banco de Dados:")
    print("   • Host: localhost:5432")
    print("   • Banco: regulacao_db")
    print("   • Usuário: regulacao_user")
    
    print("\n📱 App React Native:")
    print("   • Diretório: regulacao-app/")
    print("   • Comando: cd regulacao-app && npm start")
    
    print("\n🔧 Comandos Úteis:")
    print("   • Recarregar dados: POST /load-json-data")
    print("   • Atualizar cache: POST /refresh-data")
    print("   • Ver logs: Ctrl+C para parar")

def main():
    """Função principal"""
    print("=== SISTEMA DE REGULAÇÃO AUTÔNOMA SES-GO ===\n")
    
    # 1. Configurar PostgreSQL PATH
    print("1. Configurando PostgreSQL...")
    add_postgresql_to_path()
    
    if not check_postgresql():
        print("❌ PostgreSQL não encontrado!")
        print("Execute primeiro: python install_postgresql.py")
        return 1
    print()
    
    # 2. Testar banco de dados
    print("2. Testando banco de dados...")
    if not test_database_connection():
        print("❌ Banco de dados não configurado!")
        print("Execute primeiro: python setup_postgresql.py")
        return 1
    print()
    
    # 3. Verificar arquivos de dados
    print("3. Verificando arquivos de dados...")
    data_files = [
        'dados_em_regulacao.json',
        'dados_admitidos.json',
        'dados_alta.json',
        'dados_em_transito.json'
    ]
    
    missing_files = []
    for file in data_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Arquivos faltando: {', '.join(missing_files)}")
        return 1
    
    print("✅ Todos os arquivos de dados encontrados")
    print()
    
    # 4. Iniciar backend
    print("4. Iniciando sistema...")
    backend_process = start_backend()
    if not backend_process:
        return 1
    print()
    
    try:
        # 5. Carregar dados
        print("5. Carregando dados...")
        load_data()
        print()
        
        # 6. Testar dashboard
        print("6. Testando dashboard...")
        if not test_dashboard():
            print("❌ Dashboard com problemas")
            return 1
        
        # 7. Mostrar informações
        show_system_info()
        
        # 8. Manter rodando
        print(f"\n⏳ Sistema rodando... (Pressione Ctrl+C para parar)")
        try:
            backend_process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Parando sistema...")
            backend_process.terminate()
            backend_process.wait()
            print("✅ Sistema parado")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n🛑 Interrompido pelo usuário")
        if backend_process:
            backend_process.terminate()
            backend_process.wait()
        return 0
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        if backend_process:
            backend_process.terminate()
            backend_process.wait()
        return 1

if __name__ == "__main__":
    exit(main())