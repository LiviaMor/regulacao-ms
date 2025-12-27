"""
Script de Migração - Adicionar campos LGPD aos dados existentes
Atualiza registros antigos com valores padrão para os novos campos
"""

import sys
sys.path.insert(0, '.')

from shared.database import SessionLocal, PacienteRegulacao
from datetime import datetime

def migrar_dados():
    """Atualiza registros existentes com valores padrão para campos LGPD"""
    db = SessionLocal()
    
    try:
        # Buscar todos os pacientes
        pacientes = db.query(PacienteRegulacao).all()
        
        print(f"📊 Encontrados {len(pacientes)} registros no banco")
        
        atualizados = 0
        for paciente in pacientes:
            # Verificar se precisa atualizar
            precisa_atualizar = False
            
            if not paciente.nome_completo:
                paciente.nome_completo = f"Paciente {paciente.protocolo}"
                precisa_atualizar = True
            
            if not paciente.nome_mae:
                paciente.nome_mae = "Não informado"
                precisa_atualizar = True
            
            if not paciente.cpf:
                # Gerar CPF fictício baseado no protocolo
                cpf_base = str(hash(paciente.protocolo))[-11:].zfill(11)
                paciente.cpf = cpf_base
                precisa_atualizar = True
            
            if not paciente.telefone_contato:
                paciente.telefone_contato = "62000000000"
                precisa_atualizar = True
            
            if precisa_atualizar:
                atualizados += 1
        
        if atualizados > 0:
            db.commit()
            print(f"✅ {atualizados} registros atualizados com sucesso!")
        else:
            print("✅ Todos os registros já estão atualizados!")
        
        # Mostrar alguns exemplos
        print("\n📋 Exemplos de registros:")
        for p in pacientes[:3]:
            print(f"  - {p.protocolo}: {p.nome_completo} | CPF: {p.cpf[:3]}***{p.cpf[-2:]}")
        
    except Exception as e:
        print(f"❌ Erro na migração: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🔄 Iniciando migração de dados LGPD...")
    migrar_dados()
    print("\n✅ Migração concluída!")
