"""
MS-TRANSFERENCIA - Microserviço de Logística de Transferências
Responsável por: Autorização de transferências, gestão de ambulâncias, acompanhamento de transporte
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional, List
import sys
import os
import logging

# Adicionar path para módulos compartilhados
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.database import get_db, PacienteRegulacao, TransferenciaAmbulancia, create_tables
from shared.auth import get_current_user, require_role, Usuario
from shared.utils import setup_logging, create_audit_log, validate_protocolo

# Configurar logging
logger = setup_logging("MS-Transferencia")

# Criar aplicação FastAPI
app = FastAPI(
    title="MS-Transferencia - Sistema de Regulação SES-GO",
    description="Microserviço de Logística de Transferências",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos Pydantic
class TransferenciaRequest(BaseModel):
    protocolo: str
    unidade_destino: str
    tipo_transporte: str
    observacoes: Optional[str] = None

class IniciarTransferenciaRequest(BaseModel):
    protocolo: str
    unidade_destino: str
    tipo_transporte: str
    observacoes: Optional[str] = None

class StatusTransferenciaUpdate(BaseModel):
    protocolo: str
    novo_status: str  # EM_TRANSITO, CONCLUIDA, CANCELADA
    observacoes: Optional[str] = None

@app.on_event("startup")
async def startup_event():
    """Inicialização do microserviço"""
    create_tables()
    logger.info("MS-Transferencia iniciado com sucesso")

@app.get("/")
async def root():
    return {
        "service": "MS-Transferencia",
        "status": "running",
        "version": "1.0.0",
        "description": "Microserviço de Logística de Transferências"
    }

@app.get("/health")
async def health_check():
    return {
        "service": "MS-Transferencia",
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/iniciar-transferencia")
async def iniciar_transferencia(
    request: IniciarTransferenciaRequest,
    db: Session = Depends(get_db)
):
    """Iniciar processo de transferência (chamado pelo MS-Regulacao)"""
    
    try:
        # Validar protocolo
        if not validate_protocolo(request.protocolo):
            raise HTTPException(status_code=400, detail="Protocolo inválido")
        
        logger.info(f"🚑 Iniciando transferência para protocolo: {request.protocolo}")
        
        # Buscar paciente
        paciente = db.query(PacienteRegulacao).filter(
            PacienteRegulacao.protocolo == request.protocolo
        ).first()
        
        if not paciente:
            raise HTTPException(status_code=404, detail="Paciente não encontrado")
        
        # Verificar se já existe transferência
        transferencia_existente = db.query(TransferenciaAmbulancia).filter(
            TransferenciaAmbulancia.protocolo == request.protocolo,
            TransferenciaAmbulancia.status_transferencia.in_(["SOLICITADA", "EM_TRANSITO"])
        ).first()
        
        if transferencia_existente:
            logger.warning(f"Transferência já existe para protocolo {request.protocolo}")
            return {
                "message": "Transferência já em andamento",
                "protocolo": request.protocolo,
                "status": transferencia_existente.status_transferencia
            }
        
        # Criar nova transferência
        nova_transferencia = TransferenciaAmbulancia(
            protocolo=request.protocolo,
            tipo_transporte=request.tipo_transporte,
            status_transferencia="SOLICITADA",
            unidade_origem=paciente.unidade_solicitante or "Hospital de Origem",
            unidade_destino=request.unidade_destino,
            observacoes=request.observacoes
        )
        
        db.add(nova_transferencia)
        db.commit()
        
        # Calcular previsão de chegada baseada no tipo de transporte
        previsao_chegada = datetime.utcnow()
        if request.tipo_transporte == "USA":  # Urgente
            previsao_chegada += timedelta(minutes=30)
        elif request.tipo_transporte == "USB":  # Normal
            previsao_chegada += timedelta(hours=1)
        else:  # Próprio
            previsao_chegada += timedelta(hours=2)
        
        logger.info(f"Transferência criada: ID {nova_transferencia.id} - {request.tipo_transporte}")
        
        return {
            "message": "Transferência iniciada com sucesso",
            "protocolo": request.protocolo,
            "transferencia_id": nova_transferencia.id,
            "tipo_transporte": request.tipo_transporte,
            "unidade_destino": request.unidade_destino,
            "status": "SOLICITADA",
            "previsao_chegada": previsao_chegada.isoformat(),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao iniciar transferência: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.post("/autorizar-transferencia")
async def autorizar_transferencia(
    transferencia: TransferenciaRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["REGULADOR", "ADMIN", "TRANSFERENCIA"]))
):
    """Autorizar transferência de paciente (endpoint público para compatibilidade)"""
    
    try:
        logger.info(f"🚑 Transferência autorizada por {current_user.email}: {transferencia.protocolo} -> {transferencia.unidade_destino}")
        
        # Buscar transferência existente
        transferencia_db = db.query(TransferenciaAmbulancia).filter(
            TransferenciaAmbulancia.protocolo == transferencia.protocolo,
            TransferenciaAmbulancia.status_transferencia == "SOLICITADA"
        ).first()
        
        if transferencia_db:
            # Atualizar transferência existente
            transferencia_db.status_transferencia = "EM_TRANSITO"
            transferencia_db.data_inicio_transporte = datetime.utcnow()
            transferencia_db.observacoes = transferencia.observacoes
            db.commit()
            
            return {
                "message": "Transferência autorizada e em transporte",
                "protocolo": transferencia.protocolo,
                "unidade_destino": transferencia.unidade_destino,
                "autorizado_por": current_user.nome,
                "status": "EM_TRANSITO",
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            # Criar nova transferência se não existir
            nova_transferencia = TransferenciaAmbulancia(
                protocolo=transferencia.protocolo,
                tipo_transporte=transferencia.tipo_transporte,
                status_transferencia="EM_TRANSITO",
                unidade_destino=transferencia.unidade_destino,
                data_inicio_transporte=datetime.utcnow(),
                observacoes=transferencia.observacoes
            )
            
            db.add(nova_transferencia)
            db.commit()
            
            return {
                "message": "Transferência autorizada com sucesso",
                "protocolo": transferencia.protocolo,
                "unidade_destino": transferencia.unidade_destino,
                "autorizado_por": current_user.nome,
                "status": "EM_TRANSITO",
                "timestamp": datetime.utcnow().isoformat()
            }
        
    except Exception as e:
        logger.error(f"Erro ao autorizar transferência: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.get("/fila-transferencia")
async def get_fila_transferencia(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["REGULADOR", "ADMIN", "TRANSFERENCIA"]))
):
    """Buscar fila de transferências"""
    
    try:
        # Buscar transferências
        query = db.query(TransferenciaAmbulancia)
        
        if status:
            query = query.filter(TransferenciaAmbulancia.status_transferencia == status)
        else:
            # Por padrão, mostrar apenas as ativas
            query = query.filter(
                TransferenciaAmbulancia.status_transferencia.in_(["SOLICITADA", "EM_TRANSITO"])
            )
        
        transferencias = query.order_by(
            TransferenciaAmbulancia.data_solicitacao.desc()
        ).all()
        
        resultado = []
        for t in transferencias:
            # Buscar dados do paciente
            paciente = db.query(PacienteRegulacao).filter(
                PacienteRegulacao.protocolo == t.protocolo
            ).first()
            
            resultado.append({
                "id": t.id,
                "protocolo": t.protocolo,
                "tipo_transporte": t.tipo_transporte,
                "status_transferencia": t.status_transferencia,
                "unidade_origem": t.unidade_origem,
                "unidade_destino": t.unidade_destino,
                "data_solicitacao": t.data_solicitacao.isoformat() if t.data_solicitacao else None,
                "data_inicio_transporte": t.data_inicio_transporte.isoformat() if t.data_inicio_transporte else None,
                "data_chegada": t.data_chegada.isoformat() if t.data_chegada else None,
                "observacoes": t.observacoes,
                # Dados do paciente
                "especialidade": paciente.especialidade if paciente else None,
                "classificacao_risco": paciente.classificacao_risco if paciente else None,
                "score_prioridade": paciente.score_prioridade if paciente else None
            })
        
        logger.info(f"Fila de transferência: {len(resultado)} transferências")
        return resultado
        
    except Exception as e:
        logger.error(f"Erro ao buscar fila de transferência: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.post("/atualizar-status")
async def atualizar_status_transferencia(
    update: StatusTransferenciaUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["REGULADOR", "ADMIN", "TRANSFERENCIA"]))
):
    """Atualizar status de transferência"""
    
    try:
        # Buscar transferência
        transferencia = db.query(TransferenciaAmbulancia).filter(
            TransferenciaAmbulancia.protocolo == update.protocolo,
            TransferenciaAmbulancia.status_transferencia.in_(["SOLICITADA", "EM_TRANSITO"])
        ).first()
        
        if not transferencia:
            raise HTTPException(status_code=404, detail="Transferência não encontrada")
        
        status_anterior = transferencia.status_transferencia
        transferencia.status_transferencia = update.novo_status
        transferencia.observacoes = update.observacoes
        
        # Atualizar timestamps específicos
        if update.novo_status == "EM_TRANSITO" and not transferencia.data_inicio_transporte:
            transferencia.data_inicio_transporte = datetime.utcnow()
        elif update.novo_status == "CONCLUIDA":
            transferencia.data_chegada = datetime.utcnow()
            
            # Atualizar status do paciente para INTERNADA
            paciente = db.query(PacienteRegulacao).filter(
                PacienteRegulacao.protocolo == update.protocolo
            ).first()
            if paciente:
                paciente.status = "INTERNADA"
                paciente.updated_at = datetime.utcnow()
        
        db.commit()
        
        logger.info(f"Status transferência atualizado: {update.protocolo} - {status_anterior} -> {update.novo_status}")
        
        return {
            "message": f"Status atualizado para {update.novo_status}",
            "protocolo": update.protocolo,
            "status_anterior": status_anterior,
            "status_atual": update.novo_status,
            "atualizado_por": current_user.nome,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar status: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.get("/estatisticas")
async def estatisticas_transferencia(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["REGULADOR", "ADMIN", "TRANSFERENCIA"]))
):
    """Estatísticas de transferências"""
    
    try:
        # Contar por status
        solicitadas = db.query(TransferenciaAmbulancia).filter(
            TransferenciaAmbulancia.status_transferencia == "SOLICITADA"
        ).count()
        
        em_transito = db.query(TransferenciaAmbulancia).filter(
            TransferenciaAmbulancia.status_transferencia == "EM_TRANSITO"
        ).count()
        
        concluidas = db.query(TransferenciaAmbulancia).filter(
            TransferenciaAmbulancia.status_transferencia == "CONCLUIDA"
        ).count()
        
        canceladas = db.query(TransferenciaAmbulancia).filter(
            TransferenciaAmbulancia.status_transferencia == "CANCELADA"
        ).count()
        
        # Contar por tipo de transporte
        usa_count = db.query(TransferenciaAmbulancia).filter(
            TransferenciaAmbulancia.tipo_transporte == "USA"
        ).count()
        
        usb_count = db.query(TransferenciaAmbulancia).filter(
            TransferenciaAmbulancia.tipo_transporte == "USB"
        ).count()
        
        # Tempo médio de transporte (transferências concluídas)
        transferencias_concluidas = db.query(TransferenciaAmbulancia).filter(
            TransferenciaAmbulancia.status_transferencia == "CONCLUIDA",
            TransferenciaAmbulancia.data_inicio_transporte.isnot(None),
            TransferenciaAmbulancia.data_chegada.isnot(None)
        ).all()
        
        tempo_medio_transporte = 0
        if transferencias_concluidas:
            tempos = []
            for t in transferencias_concluidas:
                if t.data_inicio_transporte and t.data_chegada:
                    tempo = (t.data_chegada - t.data_inicio_transporte).total_seconds() / 60  # minutos
                    tempos.append(tempo)
            
            if tempos:
                tempo_medio_transporte = sum(tempos) / len(tempos)
        
        return {
            "estatisticas": {
                "por_status": {
                    "solicitadas": solicitadas,
                    "em_transito": em_transito,
                    "concluidas": concluidas,
                    "canceladas": canceladas
                },
                "por_tipo_transporte": {
                    "usa_suporte_avancado": usa_count,
                    "usb_suporte_basico": usb_count
                },
                "tempo_medio_transporte_minutos": round(tempo_medio_transporte, 2),
                "total_transferencias": solicitadas + em_transito + concluidas + canceladas
            },
            "usuario": {
                "nome": current_user.nome,
                "tipo": current_user.tipo_usuario
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erro ao buscar estatísticas: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.get("/pacientes-aguardando-ambulancia")
async def pacientes_aguardando_ambulancia(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Lista pacientes aguardando ambulância (para aba Transferência do frontend)"""
    
    try:
        # Buscar pacientes com status INTERNACAO_AUTORIZADA
        pacientes = db.query(PacienteRegulacao).filter(
            PacienteRegulacao.status == 'INTERNACAO_AUTORIZADA'
        ).order_by(PacienteRegulacao.updated_at.desc()).all()
        
        resultado = []
        for paciente in pacientes:
            # Buscar transferência associada
            transferencia = db.query(TransferenciaAmbulancia).filter(
                TransferenciaAmbulancia.protocolo == paciente.protocolo
            ).order_by(TransferenciaAmbulancia.data_solicitacao.desc()).first()
            
            resultado.append({
                "protocolo": paciente.protocolo,
                "especialidade": paciente.especialidade,
                "unidade_destino": paciente.unidade_destino,
                "classificacao_risco": paciente.classificacao_risco,
                "score_prioridade": paciente.score_prioridade,
                "data_autorizacao": paciente.updated_at.isoformat() if paciente.updated_at else None,
                "status_transferencia": transferencia.status_transferencia if transferencia else "PENDENTE",
                "tipo_transporte": transferencia.tipo_transporte if transferencia else "USB",
                "data_inicio_transporte": transferencia.data_inicio_transporte.isoformat() if transferencia and transferencia.data_inicio_transporte else None,
                "observacoes": transferencia.observacoes if transferencia else None
            })
        
        logger.info(f"Pacientes aguardando ambulância: {len(resultado)}")
        return resultado
        
    except Exception as e:
        logger.error(f"Erro ao buscar pacientes aguardando ambulância: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)