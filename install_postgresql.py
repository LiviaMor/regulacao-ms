#!/usr/bin/env python3
"""
Script para instalar PostgreSQL no Windows
"""

import subprocess
import sys
import os
import urllib.request
import tempfile
from pathlib import Path

def check_winget():
    """Verifica se winget está disponível"""
    try:
        result = subprocess.run(['winget', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Winget disponível: {result.stdout.strip()}")
            return True
        else:
            return False
    except FileNotFoundError:
        return False

def check_chocolatey():
    """Verifica se Chocolatey está disponível"""
    try:
        result = subprocess.run(['choco', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Chocolatey disponível: {result.stdout.strip()}")
            return True
        else:
            return False
    except FileNotFoundError:
        return False

def install_with_winget():
    """Instala PostgreSQL usando winget"""
    try:
        print("🔄 Instalando PostgreSQL com winget...")
        result = subprocess.run([
            'winget', 'install', 'PostgreSQL.PostgreSQL', '--accept-package-agreements', '--accept-source-agreements'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ PostgreSQL instalado com winget!")
            return True
        else:
            print(f"❌ Erro no winget: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Erro ao usar winget: {e}")
        return False

def install_with_chocolatey():
    """Instala PostgreSQL usando Chocolatey"""
    try:
        print("🔄 Instalando PostgreSQL com Chocolatey...")
        result = subprocess.run([
            'choco', 'install', 'postgresql', '-y'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ PostgreSQL instalado com Chocolatey!")
            return True
        else:
            print(f"❌ Erro no Chocolatey: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Erro ao usar Chocolatey: {e}")
        return False

def download_postgresql_installer():
    """Baixa o instalador oficial do PostgreSQL"""
    try:
        print("🔄 Baixando instalador oficial do PostgreSQL...")
        
        # URL do PostgreSQL 15 para Windows x64
        url = "https://get.enterprisedb.com/postgresql/postgresql-15.8-1-windows-x64.exe"
        
        # Criar diretório temporário
        temp_dir = tempfile.gettempdir()
        installer_path = os.path.join(temp_dir, "postgresql-installer.exe")
        
        print(f"   Baixando de: {url}")
        print(f"   Salvando em: {installer_path}")
        
        urllib.request.urlretrieve(url, installer_path)
        
        if os.path.exists(installer_path):
            print("✅ Download concluído!")
            return installer_path
        else:
            print("❌ Falha no download")
            return None
            
    except Exception as e:
        print(f"❌ Erro no download: {e}")
        return None

def run_installer(installer_path):
    """Executa o instalador do PostgreSQL"""
    try:
        print("🔄 Executando instalador...")
        print("\n⚠️ IMPORTANTE:")
        print("   1. Durante a instalação, anote a SENHA do usuário 'postgres'")
        print("   2. Use uma senha simples como 'postgres' ou 'admin'")
        print("   3. Mantenha a porta padrão 5432")
        print("   4. Instale todos os componentes")
        
        input("\nPressione Enter para continuar com a instalação...")
        
        # Executar instalador
        result = subprocess.run([installer_path], shell=True)
        
        if result.returncode == 0:
            print("✅ Instalação concluída!")
            return True
        else:
            print("⚠️ Instalador fechado (pode ter sido bem-sucedido)")
            return True  # Assumir sucesso pois o usuário pode ter fechado
            
    except Exception as e:
        print(f"❌ Erro ao executar instalador: {e}")
        return False

def setup_environment():
    """Configura variáveis de ambiente"""
    try:
        # Caminhos comuns do PostgreSQL
        common_paths = [
            r"C:\Program Files\PostgreSQL\15\bin",
            r"C:\Program Files\PostgreSQL\14\bin",
            r"C:\Program Files\PostgreSQL\13\bin",
            r"C:\Program Files (x86)\PostgreSQL\15\bin",
            r"C:\Program Files (x86)\PostgreSQL\14\bin"
        ]
        
        postgres_path = None
        for path in common_paths:
            if os.path.exists(path):
                postgres_path = path
                break
        
        if postgres_path:
            print(f"✅ PostgreSQL encontrado em: {postgres_path}")
            
            # Verificar se já está no PATH
            current_path = os.environ.get('PATH', '')
            if postgres_path not in current_path:
                print("🔄 Adicionando ao PATH da sessão atual...")
                os.environ['PATH'] = f"{postgres_path};{current_path}"
                print("✅ PATH atualizado para esta sessão")
                
                print("\n⚠️ IMPORTANTE:")
                print("   Para tornar permanente, adicione manualmente ao PATH do sistema:")
                print(f"   {postgres_path}")
            else:
                print("✅ PostgreSQL já está no PATH")
            
            return True
        else:
            print("❌ PostgreSQL não encontrado nos caminhos comuns")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao configurar ambiente: {e}")
        return False

def main():
    """Função principal"""
    print("=== INSTALAÇÃO DO POSTGRESQL NO WINDOWS ===\n")
    
    print("Este script tentará instalar o PostgreSQL usando diferentes métodos:\n")
    print("1. Winget (Gerenciador de pacotes do Windows)")
    print("2. Chocolatey (Se disponível)")
    print("3. Download do instalador oficial")
    
    choice = input("\nDeseja continuar? (s/N): ").strip().lower()
    if choice not in ['s', 'sim', 'y', 'yes']:
        print("Instalação cancelada.")
        return 0
    
    print("\n" + "="*50)
    
    # Método 1: Winget
    if check_winget():
        if install_with_winget():
            setup_environment()
            print("\n🎉 PostgreSQL instalado com sucesso via Winget!")
            print("\nExecute agora: python setup_postgresql.py")
            return 0
    
    # Método 2: Chocolatey
    if check_chocolatey():
        if install_with_chocolatey():
            setup_environment()
            print("\n🎉 PostgreSQL instalado com sucesso via Chocolatey!")
            print("\nExecute agora: python setup_postgresql.py")
            return 0
    
    # Método 3: Download manual
    print("\n🔄 Tentando download do instalador oficial...")
    installer_path = download_postgresql_installer()
    
    if installer_path:
        if run_installer(installer_path):
            setup_environment()
            
            # Limpar arquivo temporário
            try:
                os.remove(installer_path)
            except:
                pass
            
            print("\n🎉 PostgreSQL instalado!")
            print("\n📋 Próximos passos:")
            print("   1. Reinicie o terminal/PowerShell")
            print("   2. Execute: python setup_postgresql.py")
            print("   3. Use a senha que você definiu durante a instalação")
            return 0
    
    # Se chegou aqui, nada funcionou
    print("\n❌ Não foi possível instalar automaticamente.")
    print("\n📋 Instalação manual:")
    print("   1. Acesse: https://www.postgresql.org/download/windows/")
    print("   2. Baixe o instalador para Windows")
    print("   3. Execute e siga as instruções")
    print("   4. Anote a senha do usuário 'postgres'")
    print("   5. Execute: python setup_postgresql.py")
    
    return 1

if __name__ == "__main__":
    exit(main())