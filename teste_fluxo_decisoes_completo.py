#!/usr/bin/env python3
"""Teste do fluxo completo das decisões do regulador"""

import requests
import json
import time

# Configuração
API_BASE = "http://localhost:8000"

def fazer_login():
    """Fazer login como admin"""
    response = requests.post(f"{API_BASE}/login", json={
        "email": "admin@sesgo.gov.br",
        "senha": "admin123"
    })
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print("✅ Login realizado com sucesso")
        return token
    else:
        print(f"❌ Erro no login: {response.text}")
        return None

def inserir_paciente_hospital(token, protocolo_suffix="001"):
    """Inserir paciente na área hospitalar"""
    
    # Dados do paciente
    paciente_data = {
        "protocolo": f"TESTE-DECISOES-{protocolo_suffix}",
        "especialidade": "CARDIOLOGIA",
        "cid": "I21.0",
        "cid_desc": "Infarto agudo do miocárdio",
        "prontuario_texto": "Paciente masculino, 65 anos, com dor torácica intensa há 3 horas, sudorese profusa, dispneia e náuseas. Dor em aperto, irradiando para braço esquerdo e mandíbula. Histórico de hipertensão arterial e diabetes.",
        "historico_paciente": "Hipertensão arterial há 15 anos, diabetes mellitus tipo 2, tabagismo por 30 anos (parou há 5 anos), sedentarismo",
        "prioridade_descricao": "Urgente"
    }
    
    print(f"📤 Inserindo paciente {paciente_data['protocolo']} na área hospitalar...")
    
    # Primeiro processar com IA
    response_ia = requests.post(f"{API_BASE}/processar-regulacao", json=paciente_data)
    
    if response_ia.status_code == 200:
        sugestao_ia = response_ia.json()
        print(f"✅ IA processou: {sugestao_ia['analise_decisoria']['classificacao_risco']} - Score {sugestao_ia['analise_decisoria']['score_prioridade']}/10")
        
        # Salvar paciente no hospital
        response_salvar = requests.post(f"{API_BASE}/salvar-paciente-hospital", json={
            "paciente": paciente_data,
            "sugestao_ia": sugestao_ia
        })
        
        if response_salvar.status_code == 200:
            print(f"✅ Paciente {paciente_data['protocolo']} salvo na área hospitalar")
            return paciente_data["protocolo"], sugestao_ia
        else:
            print(f"❌ Erro ao salvar paciente: {response_salvar.text}")
            return None, None
    else:
        print(f"❌ Erro na IA: {response_ia.text}")
        return None, None

def listar_fila_regulacao(token):
    """Listar pacientes na fila de regulação"""
    response = requests.get(f"{API_BASE}/pacientes-hospital-aguardando", headers={
        "Authorization": f"Bearer {token}"
    })
    
    if response.status_code == 200:
        pacientes = response.json()
        print(f"📋 Fila de regulação: {len(pacientes)} paciente(s)")
        return pacientes
    else:
        print(f"❌ Erro ao buscar fila: {response.text}")
        return []

def testar_decisao_autorizar(token, protocolo, sugestao_ia):
    """Testar decisão AUTORIZAR"""
    print("\n🟢 TESTANDO DECISÃO: AUTORIZAR")
    
    decisao = {
        "protocolo": protocolo,
        "decisao_regulador": "AUTORIZADA",
        "unidade_destino": sugestao_ia["analise_decisoria"]["unidade_destino_sugerida"],
        "tipo_transporte": sugestao_ia["logistica"]["tipo_transporte"],
        "observacoes": f"Autorizada pelo regulador - Score IA: {sugestao_ia['analise_decisoria']['score_prioridade']}/10",
        "decisao_ia_original": sugestao_ia,
        "justificativa_negacao": None
    }
    
    response = requests.post(f"{API_BASE}/decisao-regulador", 
                           json=decisao,
                           headers={"Authorization": f"Bearer {token}"})
    
    if response.status_code == 200:
        resultado = response.json()
        print(f"✅ Decisão AUTORIZADA registrada: {resultado['message']}")
        return True
    else:
        print(f"❌ Erro na decisão: {response.text}")
        return False

def testar_decisao_negar(token, protocolo, sugestao_ia):
    """Testar decisão NEGAR"""
    print("\n🔴 TESTANDO DECISÃO: NEGAR")
    
    decisao = {
        "protocolo": protocolo,
        "decisao_regulador": "NEGADA",
        "unidade_destino": sugestao_ia["analise_decisoria"]["unidade_destino_sugerida"],
        "tipo_transporte": sugestao_ia["logistica"]["tipo_transporte"],
        "observacoes": f"Negada pelo regulador - Motivo: Paciente estável, pode aguardar vaga local",
        "decisao_ia_original": sugestao_ia,
        "justificativa_negacao": "Paciente estável, pode aguardar vaga local"
    }
    
    response = requests.post(f"{API_BASE}/decisao-regulador", 
                           json=decisao,
                           headers={"Authorization": f"Bearer {token}"})
    
    if response.status_code == 200:
        resultado = response.json()
        print(f"✅ Decisão NEGADA registrada: {resultado['message']}")
        return True
    else:
        print(f"❌ Erro na decisão: {response.text}")
        return False

def testar_decisao_alterar(token, protocolo, sugestao_ia):
    """Testar decisão ALTERAR"""
    print("\n🟡 TESTANDO DECISÃO: ALTERAR")
    
    novo_hospital = "HOSPITAL DE URGENCIAS DE GOIAS DR VALDEMIRO CRUZ HUGO"
    
    decisao = {
        "protocolo": protocolo,
        "decisao_regulador": "AUTORIZADA",
        "unidade_destino": novo_hospital,
        "tipo_transporte": sugestao_ia["logistica"]["tipo_transporte"],
        "observacoes": f"ALTERADA pelo regulador - Hospital original: {sugestao_ia['analise_decisoria']['unidade_destino_sugerida']} → Novo: {novo_hospital}",
        "decisao_ia_original": sugestao_ia,
        "justificativa_negacao": None
    }
    
    response = requests.post(f"{API_BASE}/decisao-regulador", 
                           json=decisao,
                           headers={"Authorization": f"Bearer {token}"})
    
    if response.status_code == 200:
        resultado = response.json()
        print(f"✅ Decisão ALTERADA registrada: {resultado['message']}")
        return True
    else:
        print(f"❌ Erro na decisão: {response.text}")
        return False

def main():
    print("🏥 TESTE FLUXO COMPLETO DAS DECISÕES DO REGULADOR")
    print("=" * 60)
    
    # 1. Login
    token = fazer_login()
    if not token:
        return
    
    # 2. Inserir paciente
    protocolo, sugestao_ia = inserir_paciente_hospital(token, "001")
    if not protocolo:
        return
    
    # 3. Verificar fila
    time.sleep(1)
    pacientes = listar_fila_regulacao(token)
    
    # 4. Testar AUTORIZAR
    if testar_decisao_autorizar(token, protocolo, sugestao_ia):
        print("✅ Fluxo AUTORIZAR funcionando")
    
    # 5. Inserir novo paciente para testar NEGAR
    print("\n" + "="*40)
    protocolo2, sugestao_ia2 = inserir_paciente_hospital(token, "002")
    if protocolo2:
        if testar_decisao_negar(token, protocolo2, sugestao_ia2):
            print("✅ Fluxo NEGAR funcionando")
    
    # 6. Inserir novo paciente para testar ALTERAR
    print("\n" + "="*40)
    protocolo3, sugestao_ia3 = inserir_paciente_hospital(token, "003")
    if protocolo3:
        if testar_decisao_alterar(token, protocolo3, sugestao_ia3):
            print("✅ Fluxo ALTERAR funcionando")
    
    print("\n" + "=" * 60)
    print("🏁 TESTE COMPLETO FINALIZADO!")

if __name__ == "__main__":
    main()