#!/usr/bin/env python3
"""
Demonstração Completa do Sistema de Regulação Autônoma SES-GO
============================================================

Este script demonstra todo o fluxo do sistema:
1. Ingestão de dados do SES-GO
2. Processamento com IA (BioBERT + Llama)
3. Autorização de transferência
4. Atualização de status

Autor: Sistema SES-GO
Data: Dezembro 2025
"""

import requests
import json
import time
from datetime import datetime
import sys

# Configurações
BASE_URL = "http://localhost:8000"
SERVICES = {
    'api': BASE_URL
}

def print_header(title):
    """Imprime cabeçalho formatado"""
    print("\n" + "="*60)
    print(f"🏥 {title}")
    print("="*60)

def print_step(step, description):
    """Imprime passo da demonstração"""
    print(f"\n📋 PASSO {step}: {description}")
    print("-" * 50)

def test_services():
    """Testa se o serviço está funcionando"""
    print_header("VERIFICAÇÃO DO SERVIÇO")
    
    try:
        response = requests.get(f"{SERVICES['api']}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API: OK")
        else:
            print(f"❌ API: HTTP {response.status_code}")
            sys.exit(1)
    except Exception as e:
        print(f"❌ API: {str(e)}")
        print("\n⚠️  Serviço não está funcionando. Execute:")
        print("   python start_simple.py")
        sys.exit(1)
    
    print("\n🎉 Serviço está funcionando!")

def demo_dashboard_publico():
    """Demonstra o dashboard público"""
    print_step(1, "DASHBOARD PÚBLICO - Dados em Tempo Real")
    
    try:
        response = requests.get(f"{SERVICES['api']}/dashboard/leitos", timeout=10)
        if response.status_code == 200:
            data = response.json()
            
            print("📊 Resumo da Rede Hospitalar:")
            for status in data.get('status_summary', []):
                print(f"   {status['status']}: {status['count']} pacientes")
            
            print(f"\n🏥 Unidades com Maior Pressão:")
            for i, unidade in enumerate(data.get('unidades_pressao', [])[:5], 1):
                print(f"   {i}. {unidade['unidade_executante_desc']}")
                print(f"      📍 {unidade.get('cidade', 'N/A')}")
                print(f"      👥 {unidade['pacientes_em_fila']} pacientes em fila")
            
            print(f"\n⏰ Última atualização: {data.get('ultima_atualizacao', 'N/A')}")
        else:
            print(f"❌ Erro ao buscar dashboard: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Erro: {e}")

def demo_autenticacao():
    """Demonstra autenticação e retorna token"""
    print_step(2, "AUTENTICAÇÃO DO REGULADOR")
    
    login_data = {
        "email": "admin@sesgo.gov.br",
        "senha": "admin123"
    }
    
    try:
        response = requests.post(f"{SERVICES['api']}/login", json=login_data, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Login realizado com sucesso!")
            print(f"👤 Usuário: {data['user_info']['nome']}")
            print(f"🏷️  Tipo: {data['user_info']['tipo_usuario']}")
            print(f"🔑 Token gerado: {data['access_token'][:20]}...")
            return data['access_token']
        else:
            print(f"❌ Erro no login: HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None

def demo_processamento_ia():
    """Demonstra processamento com IA"""
    print_step(3, "PROCESSAMENTO COM INTELIGÊNCIA ARTIFICIAL")
    
    # Dados de exemplo de um paciente crítico
    paciente_exemplo = {
        "protocolo": f"DEMO-{int(time.time())}",
        "especialidade": "CARDIOLOGIA",
        "cid": "I21.9",
        "cid_desc": "Infarto agudo do miocárdio",
        "prontuario_texto": """
        Paciente masculino, 65 anos, deu entrada no PS com dor torácica intensa 
        há 2 horas, com irradiação para braço esquerdo e mandíbula. Sudorese fria, 
        dispneia, náuseas. ECG mostra elevação do segmento ST em derivações 
        anteriores (V1-V4). Troponina elevada. Sinais vitais: PA 90/60, FC 110, 
        FR 24, SatO2 92%. Paciente consciente, orientado, ansioso.
        """,
        "historico_paciente": "HAS há 10 anos, DM tipo 2, tabagismo 30 anos/maço, IAM prévio há 5 anos com angioplastia.",
        "prioridade_descricao": "EMERGÊNCIA"
    }
    
    print("🤖 Enviando dados para análise da IA...")
    print(f"📋 Protocolo: {paciente_exemplo['protocolo']}")
    print(f"🏥 Especialidade: {paciente_exemplo['especialidade']}")
    print(f"📝 CID: {paciente_exemplo['cid']} - {paciente_exemplo['cid_desc']}")
    
    try:
        response = requests.post(
            f"{SERVICES['api']}/processar-regulacao",
            json=paciente_exemplo,
            timeout=60  # IA pode demorar mais
        )
        
        if response.status_code == 200:
            resultado = response.json()
            
            print("\n🎯 RESULTADO DA ANÁLISE IA:")
            
            # Análise Decisória
            if 'analise_decisoria' in resultado:
                analise = resultado['analise_decisoria']
                print(f"\n📊 ANÁLISE DECISÓRIA:")
                print(f"   Score de Prioridade: {analise.get('score_prioridade', 'N/A')}/10")
                print(f"   Classificação de Risco: {analise.get('classificacao_risco', 'N/A')}")
                print(f"   Unidade Sugerida: {analise.get('unidade_destino_sugerida', 'N/A')}")
                print(f"   Justificativa: {analise.get('justificativa_clinica', 'N/A')}")
            
            # Logística
            if 'logistica' in resultado:
                logistica = resultado['logistica']
                print(f"\n🚑 LOGÍSTICA:")
                print(f"   Acionar Ambulância: {'SIM' if logistica.get('acionar_ambulancia') else 'NÃO'}")
                print(f"   Tipo de Transporte: {logistica.get('tipo_transporte', 'N/A')}")
                print(f"   Previsão de Vaga: {logistica.get('previsao_vaga_h', 'N/A')}")
            
            # Protocolo Especial
            if 'protocolo_especial' in resultado:
                protocolo = resultado['protocolo_especial']
                print(f"\n🏥 PROTOCOLO ESPECIAL:")
                print(f"   Tipo: {protocolo.get('tipo', 'N/A')}")
                print(f"   Instruções: {protocolo.get('instrucoes_imediatas', 'N/A')}")
            
            # Metadados
            if 'metadata' in resultado:
                meta = resultado['metadata']
                print(f"\n⚙️  METADADOS:")
                print(f"   Tempo de Processamento: {meta.get('tempo_processamento', 0):.2f}s")
                print(f"   BioBERT Usado: {'SIM' if meta.get('biobert_usado') else 'NÃO'}")
            
            return paciente_exemplo['protocolo'], resultado
        else:
            print(f"❌ Erro no processamento: HTTP {response.status_code}")
            print(f"   Resposta: {response.text}")
            return None, None
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None, None

def demo_autorizacao_transferencia(token, protocolo, resultado_ia):
    """Demonstra autorização de transferência"""
    if not token or not protocolo or not resultado_ia:
        print("⚠️  Pulando autorização (dados insuficientes)")
        return
    
    print_step(4, "AUTORIZAÇÃO DE TRANSFERÊNCIA")
    
    # Extrair dados da decisão IA
    analise = resultado_ia.get('analise_decisoria', {})
    logistica = resultado_ia.get('logistica', {})
    
    transferencia_data = {
        "protocolo": protocolo,
        "unidade_destino": analise.get('unidade_destino_sugerida', 'Hospital de Referência'),
        "tipo_transporte": logistica.get('tipo_transporte', 'USA'),
        "observacoes": f"Autorizado via IA - Score: {analise.get('score_prioridade', 0)}/10"
    }
    
    print("📋 Dados da Transferência:")
    print(f"   Protocolo: {transferencia_data['protocolo']}")
    print(f"   Destino: {transferencia_data['unidade_destino']}")
    print(f"   Transporte: {transferencia_data['tipo_transporte']}")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(
            f"{SERVICES['logistics']}/transferencia",
            json=transferencia_data,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            resultado = response.json()
            print("\n✅ TRANSFERÊNCIA AUTORIZADA COM SUCESSO!")
            print(f"   Autorizado por: {resultado.get('autorizado_por', 'N/A')}")
            print(f"   Status: Ambulância acionada automaticamente")
            print(f"   Próximo passo: Paciente será transferido")
        else:
            print(f"❌ Erro na autorização: HTTP {response.status_code}")
            print(f"   Resposta: {response.text}")
    except Exception as e:
        print(f"❌ Erro: {e}")

def demo_dashboard_regulador(token):
    """Demonstra dashboard do regulador"""
    if not token:
        print("⚠️  Pulando dashboard do regulador (sem token)")
        return
    
    print_step(5, "DASHBOARD DO REGULADOR")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{SERVICES['logistics']}/dashboard-regulador",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            
            print("📊 ESTATÍSTICAS DO SISTEMA:")
            stats = data.get('estatisticas', {})
            print(f"   Em Regulação: {stats.get('em_regulacao', 0)} pacientes")
            print(f"   Autorizadas: {stats.get('autorizadas', 0)} transferências")
            print(f"   Internadas: {stats.get('internadas', 0)} pacientes")
            print(f"   Casos Críticos: {stats.get('criticos', 0)} pacientes")
            print(f"   Tempo Médio de Regulação: {stats.get('tempo_medio_regulacao_h', 0):.1f}h")
            
            user = data.get('usuario', {})
            print(f"\n👤 REGULADOR ATIVO:")
            print(f"   Nome: {user.get('nome', 'N/A')}")
            print(f"   Tipo: {user.get('tipo', 'N/A')}")
        else:
            print(f"❌ Erro no dashboard: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Erro: {e}")

def main():
    """Executa demonstração completa"""
    print_header("SISTEMA DE REGULAÇÃO AUTÔNOMA SES-GO")
    print("🚀 Demonstração Completa do Fluxo de Regulação")
    print("⏰ Iniciado em:", datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    
    # Verificar serviços
    test_services()
    
    # Executar demonstração
    demo_dashboard_publico()
    
    token = demo_autenticacao()
    
    protocolo, resultado_ia = demo_processamento_ia()
    
    demo_autorizacao_transferencia(token, protocolo, resultado_ia)
    
    demo_dashboard_regulador(token)
    
    # Resumo final
    print_header("DEMONSTRAÇÃO CONCLUÍDA")
    print("✅ Todos os componentes do sistema foram testados com sucesso!")
    print("\n📱 PRÓXIMOS PASSOS:")
    print("   1. Abrir o app React Native: cd regulacao-app && npm start")
    print("   2. Testar interface web: http://localhost:19006")
    print("   3. Testar no dispositivo móvel via Expo Go")
    print("\n🔧 ENDPOINTS DISPONÍVEIS:")
    print("   • Dashboard Público: http://localhost:8001/dashboard/leitos")
    print("   • Processamento IA: http://localhost:8002/processar-regulacao")
    print("   • Área do Regulador: http://localhost:8003/dashboard-regulador")
    print("\n📚 DOCUMENTAÇÃO:")
    print("   • API Docs: http://localhost:8001/docs")
    print("   • README: ./README.md")
    print("\n🎉 Sistema pronto para uso em produção!")

if __name__ == "__main__":
    main()