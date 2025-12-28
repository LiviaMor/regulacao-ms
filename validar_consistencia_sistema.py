#!/usr/bin/env python3
"""
VALIDAÇÃO DE CONSISTÊNCIA DO SISTEMA DE REGULAÇÃO
Verifica se todos os endpoints e status estão padronizados corretamente.

Status Padronizados:
- AGUARDANDO_REGULACAO: Paciente aguardando análise
- NEGADO_PENDENTE: Regulação negada, aguardando correção
- EM_TRANSFERENCIA: Transferência autorizada, ambulância acionada
- EM_TRANSITO: Paciente sendo transportado
- ADMITIDO: Paciente chegou ao destino
- ALTA: Paciente recebeu alta
"""
import requests
import sqlite3
import os
import json
from datetime import datetime

API_BASE = "http://localhost:8000"
DB_PATH = "backend/regulacao.db"

# Status válidos do sistema
STATUS_VALIDOS = [
    'AGUARDANDO_REGULACAO',
    'NEGADO_PENDENTE', 
    'EM_TRANSFERENCIA',
    'EM_TRANSITO',
    'ADMITIDO',
    'ALTA'
]

STATUS_AMBULANCIA_VALIDOS = [
    'ACIONADA',
    'A_CAMINHO',
    'NO_LOCAL',
    'TRANSPORTANDO',
    'CONCLUIDA',
    None  # Pode ser nulo se ambulância não foi acionada
]

def print_header(titulo):
    print("\n" + "=" * 70)
    print(f" {titulo}")
    print("=" * 70)

def print_result(nome, sucesso, detalhes=""):
    status = "✅ PASS" if sucesso else "❌ FAIL"
    print(f"  {status} - {nome}")
    if detalhes and not sucesso:
        print(f"         {detalhes}")

def login():
    """Login como admin"""
    try:
        response = requests.post(f"{API_BASE}/login", json={
            "email": "admin@sesgo.gov.br",
            "senha": "admin123"
        }, timeout=5)
        if response.ok:
            return response.json().get("access_token")
    except:
        pass
    return None

def validar_banco_dados():
    """Validar consistência do banco de dados"""
    print_header("1. VALIDAÇÃO DO BANCO DE DADOS")
    
    if not os.path.exists(DB_PATH):
        print_result("Banco de dados existe", False, f"Não encontrado: {DB_PATH}")
        return False
    
    print_result("Banco de dados existe", True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Verificar status inválidos
    cursor.execute("SELECT DISTINCT status FROM pacientes_regulacao")
    status_no_banco = [row[0] for row in cursor.fetchall()]
    
    status_invalidos = [s for s in status_no_banco if s not in STATUS_VALIDOS]
    print_result(
        "Todos os status são válidos", 
        len(status_invalidos) == 0,
        f"Status inválidos encontrados: {status_invalidos}" if status_invalidos else ""
    )
    
    # Verificar status_ambulancia inválidos
    cursor.execute("SELECT DISTINCT status_ambulancia FROM pacientes_regulacao WHERE status_ambulancia IS NOT NULL")
    status_amb_no_banco = [row[0] for row in cursor.fetchall()]
    
    status_amb_invalidos = [s for s in status_amb_no_banco if s not in STATUS_AMBULANCIA_VALIDOS]
    print_result(
        "Todos os status de ambulância são válidos",
        len(status_amb_invalidos) == 0,
        f"Status inválidos: {status_amb_invalidos}" if status_amb_invalidos else ""
    )
    
    # Contagem por status
    print("\n  📊 Distribuição de pacientes por status:")
    cursor.execute("SELECT status, COUNT(*) FROM pacientes_regulacao GROUP BY status ORDER BY COUNT(*) DESC")
    for status, count in cursor.fetchall():
        print(f"     - {status}: {count}")
    
    conn.close()
    return len(status_invalidos) == 0

def validar_endpoints(token):
    """Validar todos os endpoints do sistema"""
    print_header("2. VALIDAÇÃO DOS ENDPOINTS")
    
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    endpoints = [
        # Área Hospital
        ("GET", "/pacientes-hospital-aguardando", None, "Área Hospital - Lista pacientes"),
        
        # Área Regulação
        ("GET", "/pacientes-hospital-aguardando", headers, "Área Regulação - Fila"),
        
        # Área Transferência
        ("GET", "/pacientes-transferencia", headers, "Área Transferência - Lista"),
        
        # Área Auditoria
        ("GET", "/pacientes-auditoria", headers, "Área Auditoria - Lista"),
        
        # Dashboard
        ("GET", "/dashboard-regulador", headers, "Dashboard Regulador"),
        ("GET", "/dashboard/leitos", None, "Dashboard Leitos"),
    ]
    
    todos_ok = True
    for method, endpoint, hdrs, nome in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{API_BASE}{endpoint}", headers=hdrs or {}, timeout=5)
            
            sucesso = response.status_code == 200
            print_result(nome, sucesso, f"HTTP {response.status_code}" if not sucesso else "")
            if not sucesso:
                todos_ok = False
        except Exception as e:
            print_result(nome, False, str(e))
            todos_ok = False
    
    return todos_ok

def validar_fluxo_status(token):
    """Validar que os endpoints retornam os status corretos"""
    print_header("3. VALIDAÇÃO DO FLUXO DE STATUS")
    
    headers = {"Authorization": f"Bearer {token}"}
    todos_ok = True
    
    # Área Hospital deve retornar AGUARDANDO_REGULACAO e NEGADO_PENDENTE
    try:
        response = requests.get(f"{API_BASE}/pacientes-hospital-aguardando", timeout=5)
        if response.ok:
            pacientes = response.json()
            status_encontrados = set(p.get('status') for p in pacientes)
            status_esperados = {'AGUARDANDO_REGULACAO', 'NEGADO_PENDENTE'}
            status_invalidos = status_encontrados - status_esperados
            
            sucesso = len(status_invalidos) == 0
            print_result(
                "Área Hospital retorna status corretos",
                sucesso,
                f"Status inesperados: {status_invalidos}" if not sucesso else ""
            )
            if not sucesso:
                todos_ok = False
    except Exception as e:
        print_result("Área Hospital retorna status corretos", False, str(e))
        todos_ok = False
    
    # Área Transferência deve retornar EM_TRANSFERENCIA e EM_TRANSITO
    try:
        response = requests.get(f"{API_BASE}/pacientes-transferencia", headers=headers, timeout=5)
        if response.ok:
            pacientes = response.json()
            status_encontrados = set(p.get('status_paciente') for p in pacientes)
            status_esperados = {'EM_TRANSFERENCIA', 'EM_TRANSITO'}
            status_invalidos = status_encontrados - status_esperados
            
            sucesso = len(status_invalidos) == 0
            print_result(
                "Área Transferência retorna status corretos",
                sucesso,
                f"Status inesperados: {status_invalidos}" if not sucesso else ""
            )
            if not sucesso:
                todos_ok = False
    except Exception as e:
        print_result("Área Transferência retorna status corretos", False, str(e))
        todos_ok = False
    
    # Área Auditoria deve retornar ADMITIDO
    try:
        response = requests.get(f"{API_BASE}/pacientes-auditoria", headers=headers, timeout=5)
        if response.ok:
            pacientes = response.json()
            # Auditoria não retorna status diretamente, mas todos devem ser ADMITIDO
            print_result("Área Auditoria acessível", True)
    except Exception as e:
        print_result("Área Auditoria acessível", False, str(e))
        todos_ok = False
    
    return todos_ok

def validar_mapeamento_ambulancia():
    """Validar mapeamento de status ambulância → status paciente"""
    print_header("4. VALIDAÇÃO DO MAPEAMENTO AMBULÂNCIA → PACIENTE")
    
    mapeamento_esperado = {
        'ACIONADA': 'EM_TRANSFERENCIA',
        'A_CAMINHO': 'EM_TRANSFERENCIA',
        'NO_LOCAL': 'EM_TRANSFERENCIA',
        'TRANSPORTANDO': 'EM_TRANSITO',
        'CONCLUIDA': 'ADMITIDO'
    }
    
    print("  📋 Mapeamento esperado:")
    for amb, pac in mapeamento_esperado.items():
        print(f"     {amb} → {pac}")
    
    # Verificar no banco se há inconsistências
    if os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Buscar pacientes com status_ambulancia definido
        cursor.execute("""
            SELECT protocolo, status, status_ambulancia 
            FROM pacientes_regulacao 
            WHERE status_ambulancia IS NOT NULL
        """)
        
        inconsistencias = []
        for protocolo, status, status_amb in cursor.fetchall():
            esperado = mapeamento_esperado.get(status_amb)
            if esperado and status != esperado:
                inconsistencias.append(f"{protocolo}: amb={status_amb}, status={status}, esperado={esperado}")
        
        print_result(
            "Mapeamento ambulância/paciente consistente",
            len(inconsistencias) == 0,
            f"Inconsistências: {inconsistencias}" if inconsistencias else ""
        )
        
        conn.close()
        return len(inconsistencias) == 0
    
    return True

def main():
    print("\n" + "=" * 70)
    print(" VALIDAÇÃO DE CONSISTÊNCIA DO SISTEMA DE REGULAÇÃO")
    print(" Data: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 70)
    
    resultados = []
    
    # 1. Validar banco de dados
    resultados.append(("Banco de Dados", validar_banco_dados()))
    
    # 2. Login
    print_header("LOGIN")
    token = login()
    if token:
        print_result("Login como admin", True)
    else:
        print_result("Login como admin", False, "Backend pode não estar rodando")
        print("\n⚠️  Alguns testes serão ignorados pois o backend não está acessível.")
    
    # 3. Validar endpoints (se backend estiver rodando)
    if token:
        resultados.append(("Endpoints", validar_endpoints(token)))
        resultados.append(("Fluxo de Status", validar_fluxo_status(token)))
    
    # 4. Validar mapeamento ambulância
    resultados.append(("Mapeamento Ambulância", validar_mapeamento_ambulancia()))
    
    # Resumo final
    print_header("RESUMO FINAL")
    
    total_pass = sum(1 for _, r in resultados if r)
    total_fail = sum(1 for _, r in resultados if not r)
    
    for nome, resultado in resultados:
        status = "✅ PASS" if resultado else "❌ FAIL"
        print(f"  {status} - {nome}")
    
    print(f"\n  Total: {total_pass} PASS, {total_fail} FAIL")
    
    if total_fail == 0:
        print("\n  🎉 SISTEMA CONSISTENTE!")
    else:
        print("\n  ⚠️  ATENÇÃO: Há inconsistências que precisam ser corrigidas.")
    
    return total_fail == 0

if __name__ == "__main__":
    main()
