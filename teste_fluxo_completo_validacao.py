#!/usr/bin/env python3
"""
TESTE COMPLETO DE VALIDAÇÃO DO FLUXO
Valida toda a jornada do paciente: Hospital → Regulação → Transferência → Consulta
"""

import requests
import json
import time
from datetime import datetime

# Configuração
API_BASE_URL = "http://localhost:8000"
PROTOCOLO_TESTE = f"REG-2025-TEST-{int(time.time())}"

def print_header(text):
    print(f"\n{'='*80}")
    print(f"{text.center(80)}")
    print(f"{'='*80}\n")

def print_success(text):
    print(f"✅ {text}")

def print_error(text):
    print(f"❌ {text}")

def print_info(text):
    print(f"ℹ️  {text}")

# ETAPA 1: Login
def fazer_login():
    print_header("ETAPA 1: AUTENTICAÇÃO")
    try:
        response = requests.post(
            f"{API_BASE_URL}/login",
            json={"email": "admin@sesgo.gov.br", "senha": "admin123"}
        )
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            print_success(f"Login realizado: {data.get('user_info', {}).get('nome')}")
            return token
        else:
            print_error(f"Falha no login: {response.status_code}")
            return None
    except Exception as e:
        print_error(f"Erro no login: {e}")
        return None

# ETAPA 2: Inserir Paciente
def inserir_paciente(token):
    print_header("ETAPA 2: INSERIR PACIENTE (ÁREA HOSPITALAR)")
    
    # Dados do paciente para IA
    dados_paciente = {
        "protocolo": PROTOCOLO_TESTE,
        "especialidade": "CARDIOLOGIA",
        "cid": "I21.0",
        "cid_desc": "Infarto Agudo do Miocárdio",
        "prontuario_texto": "Paciente com dor torácica intensa, sudorese, dispneia. ECG com supradesnivelamento de ST.",
        "historico_paciente": "HAS, DM tipo 2",
        "prioridade_descricao": "URGENTE"
    }
    
    print_info(f"Protocolo: {PROTOCOLO_TESTE}")
    
    try:
        # Processar com IA primeiro
        response_ia = requests.post(
            f"{API_BASE_URL}/processar-regulacao",
            json=dados_paciente,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response_ia.status_code != 200:
            print_error(f"Falha no processamento IA: {response_ia.status_code}")
            return False
        
        sugestao_ia = response_ia.json()
        
        # Agora salvar paciente com sugestão da IA
        # Estrutura correta: { paciente: {...}, sugestao_ia: {...} }
        paciente_completo = {
            "protocolo": PROTOCOLO_TESTE,
            "nome_completo": "João da Silva Santos",
            "nome_mae": "Maria Santos Silva",
            "cpf": "12345678901",
            "telefone_contato": "(62) 98765-4321",
            "especialidade": "CARDIOLOGIA",
            "cid": "I21.0",
            "cid_desc": "Infarto Agudo do Miocárdio",
            "prontuario_texto": "Paciente com dor torácica intensa, sudorese, dispneia. ECG com supradesnivelamento de ST.",
            "historico_paciente": "HAS, DM tipo 2",
            "prioridade_descricao": "URGENTE",
            "cidade_origem": "GOIANIA",
            "unidade_solicitante": "HOSPITAL MUNICIPAL DE GOIANIA"
        }
        
        request_body = {
            "paciente": paciente_completo,
            "sugestao_ia": sugestao_ia
        }
        
        response = requests.post(
            f"{API_BASE_URL}/salvar-paciente-hospital",
            json=request_body,
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            print_success("Paciente inserido com sucesso!")
            return True
        else:
            print_error(f"Falha: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print_error(f"Erro: {e}")
        return False

# ETAPA 3: Verificar Fila
def verificar_fila(token):
    print_header("ETAPA 3: VERIFICAR FILA DE REGULAÇÃO")
    try:
        response = requests.get(
            f"{API_BASE_URL}/pacientes-hospital-aguardando",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            pacientes = response.json()
            encontrado = any(p.get("protocolo") == PROTOCOLO_TESTE for p in pacientes)
            if encontrado:
                print_success(f"Paciente encontrado na fila! Total: {len(pacientes)}")
                return True
            else:
                print_error("Paciente NÃO encontrado na fila")
                return False
        else:
            print_error(f"Falha: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Erro: {e}")
        return False

# ETAPA 4: Processar com IA
def processar_ia(token):
    print_header("ETAPA 4: PROCESSAR COM IA (BioBERT + Llama)")
    
    dados = {
        "protocolo": PROTOCOLO_TESTE,
        "especialidade": "CARDIOLOGIA",
        "cid": "I21.0",
        "cid_desc": "Infarto Agudo do Miocárdio",
        "prontuario_texto": "Dor torácica intensa, sudorese, dispneia. ECG com supradesnivelamento de ST.",
        "historico_paciente": "HAS, DM tipo 2",
        "prioridade_descricao": "URGENTE"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/processar-regulacao",
            json=dados,
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            decisao = response.json()
            print_success("IA processou com sucesso!")
            if "analise_decisoria" in decisao:
                ad = decisao["analise_decisoria"]
                print_info(f"Score: {ad.get('score_prioridade')}/10")
                print_info(f"Risco: {ad.get('classificacao_risco')}")
                print_info(f"Hospital: {ad.get('unidade_destino_sugerida')}")
            return decisao
        else:
            print_error(f"Falha: {response.status_code}")
            return None
    except Exception as e:
        print_error(f"Erro: {e}")
        return None

# ETAPA 5: Aprovar
def aprovar_regulacao(token, decisao_ia):
    print_header("ETAPA 5: REGULADOR APROVA")
    
    if not decisao_ia:
        print_error("Decisão IA não disponível")
        return False
    
    hospital = decisao_ia.get("analise_decisoria", {}).get("unidade_destino_sugerida", "HOSPITAL ESTADUAL DR ALBERTO RASSI")
    
    decisao = {
        "protocolo": PROTOCOLO_TESTE,
        "decisao_regulador": "AUTORIZADA",
        "unidade_destino": hospital,
        "tipo_transporte": "USA",
        "observacoes": "Aprovado pelo regulador",
        "decisao_ia_original": decisao_ia
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/decisao-regulador",
            json=decisao,
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            print_success("Regulação aprovada!")
            return True
        else:
            print_error(f"Falha: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Erro: {e}")
        return False

# ETAPA 6: Verificar Transferência
def verificar_transferencia(token):
    print_header("ETAPA 6: VERIFICAR ÁREA DE TRANSFERÊNCIA")
    try:
        response = requests.get(
            f"{API_BASE_URL}/pacientes-transferencia",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            pacientes = response.json()
            encontrado = any(p.get("protocolo") == PROTOCOLO_TESTE for p in pacientes)
            if encontrado:
                print_success(f"Paciente na transferência! Total: {len(pacientes)}")
                return True
            else:
                print_error("Paciente NÃO encontrado na transferência")
                return False
        else:
            print_error(f"Falha: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Erro: {e}")
        return False

# ETAPA 7: Solicitar Ambulância
def solicitar_ambulancia(token):
    print_header("ETAPA 7: SOLICITAR AMBULÂNCIA")
    
    dados = {
        "protocolo": PROTOCOLO_TESTE,
        "tipo_transporte": "USA",
        "observacoes": "Paciente crítico - IAM"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/solicitar-ambulancia",
            json=dados,
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            print_success("Ambulância solicitada!")
            return True
        else:
            print_error(f"Falha: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Erro: {e}")
        return False

# ETAPA 8: Consulta Pública
def consulta_publica():
    print_header("ETAPA 8: CONSULTA PÚBLICA (ANONIMIZADA)")
    try:
        response = requests.get(f"{API_BASE_URL}/consulta-publica/paciente/{PROTOCOLO_TESTE}")
        if response.status_code == 200:
            paciente = response.json()
            print_success("Paciente encontrado!")
            print_info(f"Nome: {paciente.get('nome_anonimizado')}")
            print_info(f"CPF: {paciente.get('cpf_anonimizado')}")
            print_info(f"Status: {paciente.get('status')}")
            print_info(f"Ambulância: {paciente.get('status_ambulancia')}")
            
            # Verificar anonimização
            if '*' in paciente.get('nome_anonimizado', ''):
                print_success("✓ Dados anonimizados corretamente (LGPD)")
            return True
        else:
            print_error(f"Falha: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Erro: {e}")
        return False

# EXECUTAR TESTE COMPLETO
def main():
    print_header("TESTE COMPLETO DE VALIDAÇÃO DO SISTEMA")
    print(f"Protocolo de Teste: {PROTOCOLO_TESTE}")
    print(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    resultados = {}
    
    # 1. Login
    token = fazer_login()
    resultados['login'] = token is not None
    if not token:
        print_error("TESTE ABORTADO: Falha no login")
        return
    
    # 2. Inserir Paciente
    resultados['inserir'] = inserir_paciente(token)
    time.sleep(1)
    
    # 3. Verificar Fila
    resultados['fila'] = verificar_fila(token)
    time.sleep(1)
    
    # 4. Processar IA
    decisao_ia = processar_ia(token)
    resultados['ia'] = decisao_ia is not None
    time.sleep(2)
    
    # 5. Aprovar
    resultados['aprovar'] = aprovar_regulacao(token, decisao_ia)
    time.sleep(1)
    
    # 6. Verificar Transferência
    resultados['transferencia'] = verificar_transferencia(token)
    time.sleep(1)
    
    # 7. Solicitar Ambulância
    resultados['ambulancia'] = solicitar_ambulancia(token)
    time.sleep(1)
    
    # 8. Consulta Pública
    resultados['consulta'] = consulta_publica()
    
    # RESUMO
    print_header("RESUMO DOS TESTES")
    total = len(resultados)
    sucesso = sum(1 for v in resultados.values() if v)
    
    for etapa, resultado in resultados.items():
        status = "✅ PASSOU" if resultado else "❌ FALHOU"
        print(f"{etapa.upper()}: {status}")
    
    print(f"\n{'='*80}")
    print(f"RESULTADO FINAL: {sucesso}/{total} testes passaram")
    print(f"Taxa de Sucesso: {(sucesso/total)*100:.1f}%")
    print(f"{'='*80}\n")
    
    if sucesso == total:
        print_success("🎉 TODOS OS TESTES PASSARAM! Sistema funcionando corretamente.")
    else:
        print_error(f"⚠️  {total - sucesso} teste(s) falharam. Verifique os logs acima.")

if __name__ == "__main__":
    main()
