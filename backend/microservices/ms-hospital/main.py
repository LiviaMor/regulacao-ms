"""
MS-HOSPITAL - Microserviço de Gestão Hospitalar
Responsável por: Cadastro de pacientes, solicitações de regulação, interface hospitalar
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
import sys
import os
import logging

# Adicionar path para módulos compartilhados
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.database import get_db, PacienteRegulacao, create_tables
from shared.auth import get_current_user, require_role, Usuario
from shared.utils import setup_logging, create_audit_log, validate_protocolo, MicroserviceClient

# Configurar logging
logger = setup_logging("MS-Hospital")

# Criar aplicação FastAPI
app = FastAPI(
    title="MS-Hospital - Sistema de Regulação SES-GO",
    description="Microserviço de Gestão Hospitalar",
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

# Cliente para comunicação com MS-Regulacao
ms_regulacao_client = MicroserviceClient(
    base_url=os.getenv("MS_REGULACAO_URL", "http://localhost:8002"),
    service_name="MS-Regulacao"
)

# Modelos Pydantic
class PacienteInput(BaseModel):
    protocolo: str
    solicitacao: Optional[str] = None
    especialidade: Optional[str] = None
    cid: Optional[str] = None
    cid_desc: Optional[str] = None
    prontuario_texto: Optional[str] = None
    historico_paciente: Optional[str] = None
    prioridade_descricao: Optional[str] = None

class PacienteHospitalRequest(BaseModel):
    paciente: PacienteInput
    sugestao_ia: dict

@app.on_event("startup")
async def startup_event():
    """Inicialização do microserviço"""
    create_tables()
    logger.info("MS-Hospital iniciado com sucesso")

@app.get("/")
async def root():
    return {
        "service": "MS-Hospital",
        "status": "running",
        "version": "1.0.0",
        "description": "Microserviço de Gestão Hospitalar"
    }

@app.get("/health")
async def health_check():
    return {
        "service": "MS-Hospital",
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/solicitar-regulacao")
async def solicitar_regulacao(
    paciente: PacienteInput,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Solicitar regulação para um paciente - Endpoint principal da área hospitalar"""
    
    try:
        # Validar protocolo
        if not validate_protocolo(paciente.protocolo):
            raise HTTPException(status_code=400, detail="Protocolo inválido")
        
        logger.info(f"🏥 Solicitação de regulação recebida: {paciente.protocolo}")
        
        # 1. Chamar MS-Regulacao para análise da IA
        try:
            analise_ia = ms_regulacao_client.post("/processar-regulacao", {
                "protocolo": paciente.protocolo,
                "especialidade": paciente.especialidade,
                "cid": paciente.cid,
                "cid_desc": paciente.cid_desc,
                "prontuario_texto": paciente.prontuario_texto,
                "historico_paciente": paciente.historico_paciente,
                "prioridade_descricao": paciente.prioridade_descricao
            })
        except Exception as e:
            logger.error(f"Erro ao comunicar com MS-Regulacao: {e}")
            raise HTTPException(status_code=503, detail="Serviço de regulação temporariamente indisponível")
        
        # 2. Salvar paciente no banco com status AGUARDANDO_REGULACAO
        paciente_existente = db.query(PacienteRegulacao).filter(
            PacienteRegulacao.protocolo == paciente.protocolo
        ).first()
        
        if paciente_existente:
            # Atualizar existente
            paciente_existente.especialidade = paciente.especialidade
            paciente_existente.cid = paciente.cid
            paciente_existente.cid_desc = paciente.cid_desc
            paciente_existente.prontuario_texto = paciente.prontuario_texto
            paciente_existente.historico_paciente = paciente.historico_paciente
            paciente_existente.prioridade_descricao = paciente.prioridade_descricao
            paciente_existente.status = 'AGUARDANDO_REGULACAO'
            paciente_existente.updated_at = datetime.utcnow()
            
            # Atualizar com dados da IA
            if "analise_decisoria" in analise_ia:
                paciente_existente.score_prioridade = analise_ia["analise_decisoria"].get("score_prioridade")
                paciente_existente.classificacao_risco = analise_ia["analise_decisoria"].get("classificacao_risco")
                paciente_existente.justificativa_tecnica = analise_ia["analise_decisoria"].get("justificativa_clinica")
                paciente_existente.unidade_destino = analise_ia["analise_decisoria"].get("unidade_destino_sugerida")
            
            db.commit()
            logger.info(f"Paciente {paciente.protocolo} atualizado")
            
        else:
            # Criar novo
            novo_paciente = PacienteRegulacao(
                protocolo=paciente.protocolo,
                data_solicitacao=datetime.utcnow(),
                status='AGUARDANDO_REGULACAO',
                especialidade=paciente.especialidade,
                cid=paciente.cid,
                cid_desc=paciente.cid_desc,
                prontuario_texto=paciente.prontuario_texto,
                historico_paciente=paciente.historico_paciente,
                prioridade_descricao=paciente.prioridade_descricao,
                unidade_solicitante=current_user.unidade_vinculada or "Hospital"
            )
            
            # Adicionar dados da IA
            if "analise_decisoria" in analise_ia:
                novo_paciente.score_prioridade = analise_ia["analise_decisoria"].get("score_prioridade")
                novo_paciente.classificacao_risco = analise_ia["analise_decisoria"].get("classificacao_risco")
                novo_paciente.justificativa_tecnica = analise_ia["analise_decisoria"].get("justificativa_clinica")
                novo_paciente.unidade_destino = analise_ia["analise_decisoria"].get("unidade_destino_sugerida")
            
            db.add(novo_paciente)
            db.commit()
            logger.info(f"Novo paciente {paciente.protocolo} salvo")
        
        # 3. Log de auditoria
        audit_log = create_audit_log(
            protocolo=paciente.protocolo,
            action="SOLICITACAO_REGULACAO",
            user_email=current_user.email,
            data={
                "especialidade": paciente.especialidade,
                "cid": paciente.cid,
                "score_ia": analise_ia.get("analise_decisoria", {}).get("score_prioridade"),
                "hospital_sugerido": analise_ia.get("analise_decisoria", {}).get("unidade_destino_sugerida")
            },
            microservice="MS-Hospital"
        )
        logger.info(f"Auditoria: {audit_log}")
        
        return {
            "message": "Solicitação de regulação enviada com sucesso",
            "protocolo": paciente.protocolo,
            "status": "AGUARDANDO_REGULACAO",
            "analise_ia": analise_ia,
            "hospital_sugerido": analise_ia.get("analise_decisoria", {}).get("unidade_destino_sugerida"),
            "score_prioridade": analise_ia.get("analise_decisoria", {}).get("score_prioridade"),
            "classificacao_risco": analise_ia.get("analise_decisoria", {}).get("classificacao_risco"),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao processar solicitação: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.get("/pacientes-aguardando")
async def listar_pacientes_aguardando(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Lista pacientes que foram inseridos pelo hospital e aguardam regulação"""
    
    try:
        # Buscar apenas pacientes com status 'AGUARDANDO_REGULACAO'
        pacientes = db.query(PacienteRegulacao).filter(
            PacienteRegulacao.status == 'AGUARDANDO_REGULACAO'
        ).order_by(PacienteRegulacao.data_solicitacao.desc()).all()
        
        resultado = []
        for paciente in pacientes:
            resultado.append({
                "protocolo": paciente.protocolo,
                "especialidade": paciente.especialidade,
                "cid": paciente.cid or "N/A",
                "cid_desc": paciente.cid_desc,
                "status": paciente.status,
                "data_solicitacao": paciente.data_solicitacao.isoformat() if paciente.data_solicitacao else None,
                "justificativa_tecnica": paciente.justificativa_tecnica,
                "score_prioridade": paciente.score_prioridade,
                "classificacao_risco": paciente.classificacao_risco,
                "unidade_destino": paciente.unidade_destino,
                "historico_paciente": paciente.historico_paciente,
                "prioridade_descricao": paciente.prioridade_descricao
            })
        
        logger.info(f"Retornando {len(resultado)} pacientes aguardando regulação")
        return resultado
        
    except Exception as e:
        logger.error(f"Erro ao buscar pacientes aguardando: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.post("/salvar-paciente")
async def salvar_paciente_hospital(
    request: PacienteHospitalRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Salva paciente inserido pelo hospital com sugestão da IA (compatibilidade)"""
    
    try:
        paciente = request.paciente
        sugestao_ia = request.sugestao_ia
        
        # Verificar se já existe
        paciente_existente = db.query(PacienteRegulacao).filter(
            PacienteRegulacao.protocolo == paciente.protocolo
        ).first()
        
        if paciente_existente:
            # Atualizar existente
            paciente_existente.especialidade = paciente.especialidade
            paciente_existente.cid = paciente.cid
            paciente_existente.cid_desc = paciente.cid_desc
            paciente_existente.prontuario_texto = paciente.prontuario_texto
            paciente_existente.historico_paciente = paciente.historico_paciente
            paciente_existente.prioridade_descricao = paciente.prioridade_descricao
            paciente_existente.status = 'AGUARDANDO_REGULACAO'
            paciente_existente.updated_at = datetime.utcnow()
            
            # Atualizar com dados da IA
            if "analise_decisoria" in sugestao_ia:
                paciente_existente.score_prioridade = sugestao_ia["analise_decisoria"].get("score_prioridade")
                paciente_existente.classificacao_risco = sugestao_ia["analise_decisoria"].get("classificacao_risco")
                paciente_existente.justificativa_tecnica = sugestao_ia["analise_decisoria"].get("justificativa_clinica")
                paciente_existente.unidade_destino = sugestao_ia["analise_decisoria"].get("unidade_destino_sugerida")
            
            db.commit()
            logger.info(f"Paciente {paciente.protocolo} atualizado")
            
        else:
            # Criar novo
            novo_paciente = PacienteRegulacao(
                protocolo=paciente.protocolo,
                data_solicitacao=datetime.utcnow(),
                status='AGUARDANDO_REGULACAO',
                especialidade=paciente.especialidade,
                cid=paciente.cid,
                cid_desc=paciente.cid_desc,
                prontuario_texto=paciente.prontuario_texto,
                historico_paciente=paciente.historico_paciente,
                prioridade_descricao=paciente.prioridade_descricao,
                unidade_solicitante=current_user.unidade_vinculada or "Hospital"
            )
            
            # Adicionar dados da IA
            if "analise_decisoria" in sugestao_ia:
                novo_paciente.score_prioridade = sugestao_ia["analise_decisoria"].get("score_prioridade")
                novo_paciente.classificacao_risco = sugestao_ia["analise_decisoria"].get("classificacao_risco")
                novo_paciente.justificativa_tecnica = sugestao_ia["analise_decisoria"].get("justificativa_clinica")
                novo_paciente.unidade_destino = sugestao_ia["analise_decisoria"].get("unidade_destino_sugerida")
            
            db.add(novo_paciente)
            db.commit()
            logger.info(f"Novo paciente {paciente.protocolo} salvo")
        
        return {
            "message": "Paciente salvo com sucesso",
            "protocolo": paciente.protocolo,
            "status": "AGUARDANDO_REGULACAO"
        }
        
    except Exception as e:
        logger.error(f"Erro ao salvar paciente: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.get("/estatisticas")
async def estatisticas_hospital(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Estatísticas do hospital"""
    
    try:
        # Contar pacientes por status
        total_aguardando = db.query(PacienteRegulacao).filter(
            PacienteRegulacao.status == 'AGUARDANDO_REGULACAO'
        ).count()
        
        total_autorizados = db.query(PacienteRegulacao).filter(
            PacienteRegulacao.status == 'INTERNACAO_AUTORIZADA'
        ).count()
        
        total_negados = db.query(PacienteRegulacao).filter(
            PacienteRegulacao.status == 'REGULACAO_NEGADA'
        ).count()
        
        return {
            "hospital": current_user.unidade_vinculada or "Hospital",
            "estatisticas": {
                "aguardando_regulacao": total_aguardando,
                "internacao_autorizada": total_autorizados,
                "regulacao_negada": total_negados,
                "total_solicitacoes": total_aguardando + total_autorizados + total_negados
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erro ao buscar estatísticas: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)