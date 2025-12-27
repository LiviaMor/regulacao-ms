"""
MS-REGULACAO - Microserviço de Regulação Médica - RAG READY
Responsável por: IA inteligente, pipeline de hospitais, fila de regulação, decisões
Integração com LLMs via RAG (Retrieval-Augmented Generation)
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any
import sys
import os
import logging
import json
import time

# Adicionar path para módulos compartilhados
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.database import get_db, PacienteRegulacao, HistoricoDecisoes, create_tables
from shared.auth import get_current_user, require_role, Usuario
from shared.utils import setup_logging, create_audit_log, validate_protocolo, MicroserviceClient
from shared.biobert_service import extrair_entidades_biobert, is_biobert_disponivel
from shared.matchmaker_logistico import processar_matchmaking

# Importar integração RAG
from rag_integration import processar_regulacao_rag, testar_rag_integration

# Configurar logging
logger = setup_logging("MS-Regulacao")

# Criar aplicação FastAPI
app = FastAPI(
    title="MS-Regulacao - Sistema de Regulação SES-GO - RAG Ready",
    description="Microserviço de Regulação Médica e IA com suporte a LLMs",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cliente para comunicação com MS-Transferencia
ms_transferencia_client = MicroserviceClient(
    base_url=os.getenv("MS_TRANSFERENCIA_URL", "http://localhost:8003"),
    service_name="MS-Transferencia"
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

class ProcessarRegulacaoRequest(BaseModel):
    paciente: PacienteInput
    usar_llm: Optional[bool] = False
    llm_provider: Optional[str] = "ollama"  # ollama, openai, anthropic

class DecisaoReguladorRequest(BaseModel):
    protocolo: str
    decisao_regulador: str  # 'AUTORIZADA' ou 'NEGADA'
    unidade_destino: str
    tipo_transporte: str
    observacoes: Optional[str] = None
    decisao_ia_original: dict
    justificativa_negacao: Optional[str] = None
    decisao_alterada: Optional[bool] = False  # Novo campo para indicar se foi alterada
    hospital_original: Optional[str] = None   # Hospital original da IA

# Importar pipeline de hospitais (mantido do sistema atual)
def analisar_com_ia_inteligente(paciente_data: dict) -> dict:
    """IA Inteligente com Pipeline de Hospitais de Goiás - Análise real baseada nos dados do paciente"""
    
    # Importar pipeline de hospitais
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from pipeline_hospitais_goias import selecionar_hospital_goias
    
    # Extrair dados do paciente
    protocolo = paciente_data.get('protocolo', 'N/A')
    especialidade = paciente_data.get('especialidade', '').upper()
    cid = paciente_data.get('cid', '')
    cid_desc = paciente_data.get('cid_desc', '')
    prontuario = paciente_data.get('prontuario_texto', '')
    historico = paciente_data.get('historico_paciente', '')
    prioridade_desc = paciente_data.get('prioridade_descricao', 'Normal')
    
    # Análise de Risco baseada em CID e sintomas
    score_prioridade = 5  # Base
    classificacao_risco = "AMARELO"
    justificativa_partes = []
    
    # === RESUMO DOS DADOS INSERIDOS ===
    justificativa_partes.append(f"DADOS INSERIDOS - Protocolo: {protocolo}")
    if especialidade:
        justificativa_partes.append(f"Especialidade: {especialidade}")
    if cid:
        justificativa_partes.append(f"CID: {cid} ({cid_desc})" if cid_desc else f"CID: {cid}")
    if prontuario:
        justificativa_partes.append(f"Quadro clínico: {prontuario[:100]}{'...' if len(prontuario) > 100 else ''}")
    if historico:
        justificativa_partes.append(f"Histórico: {historico[:80]}{'...' if len(historico) > 80 else ''}")
    
    # === ANÁLISE POR CID (Códigos reais de emergência) ===
    cids_criticos = {
        'I21': {'score': 9, 'risco': 'VERMELHO', 'desc': 'Infarto Agudo do Miocárdio'},
        'I46': {'score': 10, 'risco': 'VERMELHO', 'desc': 'Parada Cardíaca'},
        'G93.1': {'score': 9, 'risco': 'VERMELHO', 'desc': 'Lesão Cerebral Anóxica'},
        'R57': {'score': 9, 'risco': 'VERMELHO', 'desc': 'Choque'},
        'J44.1': {'score': 8, 'risco': 'VERMELHO', 'desc': 'DPOC com Exacerbação'},
        'N17': {'score': 8, 'risco': 'VERMELHO', 'desc': 'Insuficiência Renal Aguda'},
        'K92.2': {'score': 8, 'risco': 'VERMELHO', 'desc': 'Hemorragia Gastrointestinal'},
        'S06': {'score': 8, 'risco': 'VERMELHO', 'desc': 'Traumatismo Craniano'},
        'I63': {'score': 8, 'risco': 'VERMELHO', 'desc': 'AVC Isquêmico'},
        'I61': {'score': 9, 'risco': 'VERMELHO', 'desc': 'AVC Hemorrágico'},
        'J18': {'score': 7, 'risco': 'AMARELO', 'desc': 'Pneumonia'},
        'E11': {'score': 6, 'risco': 'AMARELO', 'desc': 'Diabetes Mellitus'},
        'I10': {'score': 5, 'risco': 'AMARELO', 'desc': 'Hipertensão Arterial'},
        'M79': {'score': 4, 'risco': 'VERDE', 'desc': 'Dor Musculoesquelética'},
        'M54': {'score': 3, 'risco': 'VERDE', 'desc': 'Dor Lombar'}
    }
    
    # Verificar CID
    cid_encontrado = None
    for cid_code, info in cids_criticos.items():
        if cid.startswith(cid_code):
            cid_encontrado = info
            score_prioridade = info['score']
            classificacao_risco = info['risco']
            justificativa_partes.append(f"ANÁLISE CID: {cid} ({info['desc']}) = RISCO {info['risco']} (Score: {info['score']}/10)")
            break
    
    if not cid_encontrado and cid:
        justificativa_partes.append(f"ANÁLISE CID: {cid} não está na base crítica, mantendo score padrão")
    
    # === ANÁLISE DE SINTOMAS NO PRONTUÁRIO ===
    sintomas_criticos = {
        'dor no peito': {'score': +3, 'desc': 'dor torácica'},
        'falta de ar': {'score': +2, 'desc': 'dispneia'},
        'inconsciência': {'score': +4, 'desc': 'alteração do nível de consciência'},
        'convulsão': {'score': +3, 'desc': 'atividade convulsiva'},
        'hemorragia': {'score': +3, 'desc': 'sangramento ativo'},
        'vômito': {'score': +1, 'desc': 'êmese'},
        'febre alta': {'score': +2, 'desc': 'hipertermia'},
        'pressão baixa': {'score': +2, 'desc': 'hipotensão'},
        'taquicardia': {'score': +2, 'desc': 'frequência cardíaca elevada'},
        'cianose': {'score': +3, 'desc': 'cianose'},
        'rebaixamento': {'score': +3, 'desc': 'rebaixamento do nível de consciência'},
        'trauma': {'score': +4, 'desc': 'traumatismo'},
        'acidente': {'score': +4, 'desc': 'trauma por acidente'}
    }
    
    prontuario_lower = prontuario.lower()
    sintomas_encontrados = []
    score_sintomas = 0
    
    for sintoma, info in sintomas_criticos.items():
        if sintoma in prontuario_lower:
            score_prioridade += info['score']
            score_sintomas += info['score']
            sintomas_encontrados.append(info['desc'])
    
    if sintomas_encontrados:
        justificativa_partes.append(f"SINTOMAS DETECTADOS: {', '.join(sintomas_encontrados)} (+{score_sintomas} pontos)")
    else:
        justificativa_partes.append("SINTOMAS: Nenhum sintoma crítico detectado no texto")
    
    # === ANÁLISE DE PRIORIDADE DECLARADA ===
    if 'urgente' in prioridade_desc.lower() or 'emergência' in prioridade_desc.lower():
        score_prioridade += 2
        justificativa_partes.append(f"PRIORIDADE: '{prioridade_desc}' = +2 pontos por urgência")
    else:
        justificativa_partes.append(f"PRIORIDADE: '{prioridade_desc}' = sem ajuste adicional")
    
    # === AJUSTAR CLASSIFICAÇÃO FINAL ===
    if score_prioridade >= 8:
        classificacao_risco = "VERMELHO"
    elif score_prioridade >= 6:
        classificacao_risco = "AMARELO"
    else:
        classificacao_risco = "VERDE"
    
    # Limitar score
    score_prioridade = min(10, max(1, score_prioridade))
    
    # === SELEÇÃO INTELIGENTE DE HOSPITAL COM PIPELINE DE GOIÁS ===
    try:
        # Usar pipeline inteligente de hospitais
        unidade_destino, motivo_escolha = selecionar_hospital_goias(
            cid=cid,
            especialidade=especialidade,
            sintomas=prontuario,
            gravidade=classificacao_risco
        )
        
        justificativa_partes.append(f"HOSPITAL SELECIONADO PELO PIPELINE: {unidade_destino}")
        justificativa_partes.append(f"JUSTIFICATIVA TÉCNICA: {motivo_escolha}")
        
    except Exception as e:
        logger.error(f"Erro no pipeline de hospitais: {e}")
        # Fallback para seleção manual
        unidade_destino = "HOSPITAL ESTADUAL DR ALBERTO RASSI HGG"
        justificativa_partes.append(f"HOSPITAL FALLBACK: {unidade_destino} - Pipeline indisponível")
    
    # === LOGÍSTICA INTELIGENTE ===
    tipo_transporte = "USB"  # Padrão
    acionar_ambulancia = True
    previsao_vaga = "2-4 horas"
    
    if classificacao_risco == "VERMELHO":
        tipo_transporte = "USA"  # Unidade de Suporte Avançado
        previsao_vaga = "Imediato"
        justificativa_partes.append("TRANSPORTE: USA (Suporte Avançado) devido ao alto risco")
    elif classificacao_risco == "AMARELO":
        tipo_transporte = "USB"  # Unidade de Suporte Básico
        previsao_vaga = "1-2 horas"
        justificativa_partes.append("TRANSPORTE: USB (Suporte Básico) adequado para o risco")
    else:
        previsao_vaga = "4-8 horas"
        if score_prioridade <= 3:
            acionar_ambulancia = False
            justificativa_partes.append("TRANSPORTE: Próprio pode ser considerado (baixo risco)")
        else:
            justificativa_partes.append("TRANSPORTE: USB (Suporte Básico) para baixo risco")
    
    # === JUSTIFICATIVA FINAL ESTRUTURADA ===
    justificativa_final = " | ".join(justificativa_partes) + f" | SCORE FINAL: {score_prioridade}/10 = RISCO {classificacao_risco}"
    
    return {
        "analise_decisoria": {
            "score_prioridade": score_prioridade,
            "classificacao_risco": classificacao_risco,
            "unidade_destino_sugerida": unidade_destino,
            "justificativa_clinica": justificativa_final
        },
        "logistica": {
            "acionar_ambulancia": acionar_ambulancia,
            "tipo_transporte": tipo_transporte,
            "previsao_vaga_h": previsao_vaga
        },
        "protocolo_especial": {
            "tipo": "NORMAL",
            "instrucoes_imediatas": "Monitorização de sinais vitais durante transporte"
        },
        "metadata": {
            "ia_engine": "IA Inteligente v3.0 - PIPELINE HOSPITAIS GOIÁS - MS-REGULACAO",
            "dados_analisados": {
                "protocolo": protocolo,
                "especialidade": especialidade,
                "cid": cid,
                "sintomas_detectados": len(sintomas_encontrados),
                "hospital_justificado": True,
                "pipeline_hospitais": True,
                "pipeline_ativo": True,
                "microservico": "MS-Regulacao"
            }
        }
    }

@app.on_event("startup")
async def startup_event():
    """Inicialização do microserviço"""
    create_tables()
    logger.info("MS-Regulacao iniciado com sucesso")

@app.get("/")
async def root():
    return {
        "service": "MS-Regulacao",
        "status": "running",
        "version": "1.0.0",
        "description": "Microserviço de Regulação Médica e IA"
    }

@app.get("/health")
async def health_check():
    return {
        "service": "MS-Regulacao",
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "biobert_disponivel": is_biobert_disponivel(),
        "pipeline_rag": True,
        "llm_suportados": ["ollama"]  # Apenas open source
    }

@app.post("/processar-regulacao")
async def processar_regulacao_ia(
    paciente: PacienteInput,
    db: Session = Depends(get_db)
):
    """Processamento com IA Inteligente + BioBERT + Matchmaker Logístico - SEMPRE FUNCIONA"""
    start_time = time.time()
    
    if not paciente.cid:
        raise HTTPException(status_code=400, detail="CID obrigatório para análise")
    
    try:
        logger.info(f"🤖 MS-Regulacao processando IA + BioBERT + Matchmaker para protocolo: {paciente.protocolo}")
        
        # 1. Análise BioBERT do prontuário
        resultado_biobert = None
        if paciente.prontuario_texto:
            try:
                biobert_analise = extrair_entidades_biobert(paciente.prontuario_texto)
                if biobert_analise["status"] == "sucesso":
                    resultado_biobert = biobert_analise["analise"]
                    logger.info(f"🧬 BioBERT: {biobert_analise['nivel_confianca']} confiança ({biobert_analise['confianca']})")
                else:
                    resultado_biobert = biobert_analise["analise"]
                    logger.warning(f"⚠️ BioBERT: {biobert_analise['status']}")
            except Exception as e:
                logger.error(f"❌ Erro BioBERT: {e}")
                resultado_biobert = "Análise BioBERT indisponível"
        
        # 2. Preparar dados do paciente para a IA
        paciente_data = {
            'protocolo': paciente.protocolo,
            'especialidade': paciente.especialidade or '',
            'cid': paciente.cid,
            'cid_desc': paciente.cid_desc or '',
            'prontuario_texto': paciente.prontuario_texto or '',
            'historico_paciente': paciente.historico_paciente or '',
            'prioridade_descricao': paciente.prioridade_descricao or 'Normal',
            'cidade_origem': 'GOIANIA'  # Default - em produção viria do hospital solicitante
        }
        
        # 3. Processar com RAG (inclui BioBERT)
        try:
            decisao = processar_regulacao_rag(paciente_data, "ollama", resultado_biobert)
            logger.info(f"✅ RAG processou: {decisao.get('hospital_escolhido', 'N/A')}")
        except Exception as e:
            logger.error(f"❌ Erro RAG: {e}")
            # Fallback para IA tradicional
            decisao = analisar_com_ia_inteligente(paciente_data)
        
        # 4. NOVO: Processar Matchmaking Logístico
        try:
            resultado_matchmaking = processar_matchmaking(paciente_data, decisao)
            logger.info(f"🚑 Matchmaker: {resultado_matchmaking['matchmaking_logistico']['distancia_km']}km - {resultado_matchmaking['matchmaking_logistico']['tempo_estimado_min']}min")
            
            # Integrar dados do matchmaking na decisão
            decisao["matchmaking_logistico"] = resultado_matchmaking["matchmaking_logistico"]
            decisao["ambulancia_sugerida"] = resultado_matchmaking["ambulancia_sugerida"]
            decisao["rota_otimizada"] = resultado_matchmaking["rota_otimizada"]
            decisao["protocolo_especial"] = resultado_matchmaking["protocolo_especial"]
            
        except Exception as e:
            logger.error(f"❌ Erro Matchmaker: {e}")
            # Continuar sem matchmaking se falhar
            decisao["matchmaking_logistico"] = {
                "erro": str(e),
                "fallback": True,
                "hospital_destino": decisao.get("analise_decisoria", {}).get("unidade_destino_sugerida", "N/A")
            }
        
        # 5. Salvar no histórico
        tempo_processamento = time.time() - start_time
        
        historico = HistoricoDecisoes(
            protocolo=paciente.protocolo,
            decisao_ia=json.dumps(decisao),
            tempo_processamento=tempo_processamento,
            microservico_origem="MS-Regulacao"
        )
        db.add(historico)
        
        # 6. Atualizar paciente se existir
        paciente_db = db.query(PacienteRegulacao).filter(
            PacienteRegulacao.protocolo == paciente.protocolo
        ).first()
        
        if paciente_db:
            if "analise_decisoria" in decisao:
                paciente_db.score_prioridade = decisao["analise_decisoria"].get("score_prioridade")
                paciente_db.classificacao_risco = decisao["analise_decisoria"].get("classificacao_risco")
                paciente_db.justificativa_tecnica = decisao["analise_decisoria"].get("justificativa_clinica")
                paciente_db.unidade_destino = decisao["analise_decisoria"].get("unidade_destino_sugerida")
            elif "hospital_escolhido" in decisao:  # Formato RAG
                paciente_db.score_prioridade = decisao.get("score_adequacao", 5)
                paciente_db.classificacao_risco = "AMARELO"  # Padrão
                paciente_db.justificativa_tecnica = decisao.get("justificativa_tecnica", "")
                paciente_db.unidade_destino = decisao.get("hospital_escolhido")
            
            paciente_db.prontuario_texto = paciente.prontuario_texto
            paciente_db.updated_at = datetime.utcnow()
        else:
            # Criar novo paciente se não existir
            novo_paciente = PacienteRegulacao(
                protocolo=paciente.protocolo,
                data_solicitacao=datetime.utcnow(),
                status='EM_REGULACAO',
                especialidade=paciente.especialidade,
                prontuario_texto=paciente.prontuario_texto,
                score_prioridade=decisao.get("analise_decisoria", {}).get("score_prioridade") or decisao.get("score_adequacao", 5),
                classificacao_risco=decisao.get("analise_decisoria", {}).get("classificacao_risco") or "AMARELO",
                justificativa_tecnica=decisao.get("analise_decisoria", {}).get("justificativa_clinica") or decisao.get("justificativa_tecnica", ""),
                unidade_destino=decisao.get("analise_decisoria", {}).get("unidade_destino_sugerida") or decisao.get("hospital_escolhido")
            )
            db.add(novo_paciente)
        
        db.commit()
        
        # 7. Adicionar metadados à resposta
        if "metadata" not in decisao:
            decisao["metadata"] = {}
        
        decisao["metadata"].update({
            "tempo_processamento": tempo_processamento,
            "timestamp": datetime.utcnow().isoformat(),
            "paciente_salvo": True,
            "biobert_usado": resultado_biobert is not None,
            "biobert_disponivel": is_biobert_disponivel(),
            "matchmaker_usado": "matchmaking_logistico" in decisao,
            "microservico": "MS-Regulacao"
        })
        
        logger.info(f"✅ MS-Regulacao processou {paciente.protocolo} em {tempo_processamento:.2f}s")
        
        return decisao
        
    except Exception as e:
        logger.error(f"❌ Erro no processamento MS-Regulacao: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.get("/fila-regulacao")
async def get_fila_regulacao(
    especialidade: Optional[str] = None,
    cidade: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["REGULADOR", "ADMIN"]))
):
    """Buscar fila de regulação - pacientes aguardando decisão do regulador"""
    
    try:
        # Buscar pacientes com status 'AGUARDANDO_REGULACAO'
        query = db.query(PacienteRegulacao).filter(
            PacienteRegulacao.status == 'AGUARDANDO_REGULACAO'
        )
        
        # Aplicar filtros
        if especialidade:
            query = query.filter(PacienteRegulacao.especialidade.ilike(f"%{especialidade}%"))
        if cidade:
            query = query.filter(PacienteRegulacao.cidade_origem.ilike(f"%{cidade}%"))
        
        # Ordenar por prioridade (score maior primeiro) e data
        pacientes = query.order_by(
            PacienteRegulacao.score_prioridade.desc(),
            PacienteRegulacao.data_solicitacao.asc()
        ).all()
        
        resultado = []
        for paciente in pacientes:
            resultado.append({
                "protocolo": paciente.protocolo,
                "data_solicitacao": paciente.data_solicitacao.isoformat() if paciente.data_solicitacao else None,
                "especialidade": paciente.especialidade,
                "cid": paciente.cid,
                "cid_desc": paciente.cid_desc,
                "cidade_origem": paciente.cidade_origem,
                "unidade_solicitante": paciente.unidade_solicitante,
                "score_prioridade": paciente.score_prioridade,
                "classificacao_risco": paciente.classificacao_risco,
                "justificativa_tecnica": paciente.justificativa_tecnica,
                "unidade_destino": paciente.unidade_destino,
                "prontuario_texto": paciente.prontuario_texto,
                "historico_paciente": paciente.historico_paciente,
                "prioridade_descricao": paciente.prioridade_descricao
            })
        
        logger.info(f"Fila de regulação: {len(resultado)} pacientes")
        return resultado
        
    except Exception as e:
        logger.error(f"Erro ao buscar fila de regulação: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.post("/decisao-regulador")
async def registrar_decisao_regulador(
    decisao: DecisaoReguladorRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["REGULADOR", "ADMIN"]))
):
    """Registrar decisão do regulador com 3 fluxos: AUTORIZAR → Transferência, NEGAR → Hospital, ALTERAR → Transferência"""
    
    try:
        # Buscar paciente
        paciente = db.query(PacienteRegulacao).filter(
            PacienteRegulacao.protocolo == decisao.protocolo
        ).first()
        
        if not paciente:
            raise HTTPException(status_code=404, detail="Paciente não encontrado")
        
        # Determinar tipo de decisão
        if decisao.decisao_alterada:
            tipo_decisao = "ALTERADA_E_AUTORIZADA"
            status_final = "INTERNACAO_AUTORIZADA"
            status_message = f"Decisão alterada e autorizada pelo regulador - Hospital alterado de '{decisao.hospital_original}' para '{decisao.unidade_destino}'"
        elif decisao.decisao_regulador == 'AUTORIZADA':
            tipo_decisao = "AUTORIZADA"
            status_final = "INTERNACAO_AUTORIZADA"
            status_message = "Transferência autorizada pelo regulador"
        else:
            tipo_decisao = "NEGADA"
            status_final = "AGUARDANDO_REGULACAO"  # Volta para fila do hospital
            status_message = f"Transferência negada pelo regulador - Motivo: {decisao.justificativa_negacao or 'Não especificado'}"

        # Registrar no histórico de decisões (AUDITORIA COMPLETA)
        historico = HistoricoDecisoes(
            protocolo=decisao.protocolo,
            decisao_ia=json.dumps(decisao.decisao_ia_original),
            usuario_validador=current_user.email,
            decisao_final=json.dumps({
                "tipo_decisao": tipo_decisao,
                "decisao_regulador": decisao.decisao_regulador,
                "unidade_destino": decisao.unidade_destino,
                "unidade_destino_original": decisao.hospital_original,
                "tipo_transporte": decisao.tipo_transporte,
                "observacoes": decisao.observacoes,
                "justificativa_negacao": decisao.justificativa_negacao,
                "decisao_alterada": decisao.decisao_alterada,
                "timestamp": datetime.utcnow().isoformat(),
                "regulador": {
                    "nome": current_user.nome,
                    "email": current_user.email,
                    "tipo_usuario": current_user.tipo_usuario
                }
            }),
            tempo_processamento=0.0,  # Decisão humana
            microservico_origem="MS-Regulacao"
        )
        db.add(historico)
        
        # Atualizar status do paciente baseado na decisão
        if status_final == "INTERNACAO_AUTORIZADA":
            paciente.status = status_final
            paciente.unidade_destino = decisao.unidade_destino
            
            # Comunicar com MS-Transferencia para iniciar logística
            try:
                ms_transferencia_client.post("/iniciar-transferencia", {
                    "protocolo": decisao.protocolo,
                    "unidade_destino": decisao.unidade_destino,
                    "tipo_transporte": decisao.tipo_transporte,
                    "observacoes": decisao.observacoes,
                    "decisao_alterada": decisao.decisao_alterada,
                    "hospital_original": decisao.hospital_original
                })
                logger.info(f"✅ MS-Transferencia notificado para protocolo {decisao.protocolo}")
            except Exception as e:
                logger.warning(f"⚠️ Erro ao comunicar com MS-Transferencia: {e}")
                
        elif status_final == "AGUARDANDO_REGULACAO":
            # NEGAR: Volta para fila do hospital
            paciente.status = status_final
            logger.info(f"❌ Paciente {decisao.protocolo} retornará à fila do hospital - Motivo: {decisao.justificativa_negacao}")
        
        paciente.updated_at = datetime.utcnow()
        db.commit()
        
        # Preparar resposta baseada no tipo de decisão
        if tipo_decisao == "ALTERADA_E_AUTORIZADA":
            response_data = {
                "message": status_message,
                "protocolo": decisao.protocolo,
                "decisao": "ALTERADA_E_AUTORIZADA",
                "unidade_destino_original": decisao.hospital_original,
                "unidade_destino_final": decisao.unidade_destino,
                "regulador": current_user.nome,
                "timestamp": datetime.utcnow().isoformat(),
                "fluxo": "HOSPITAL → REGULAÇÃO → ALTERAÇÃO → TRANSFERÊNCIA"
            }
        elif tipo_decisao == "AUTORIZADA":
            response_data = {
                "message": status_message,
                "protocolo": decisao.protocolo,
                "decisao": decisao.decisao_regulador,
                "unidade_destino": decisao.unidade_destino,
                "regulador": current_user.nome,
                "timestamp": datetime.utcnow().isoformat(),
                "fluxo": "HOSPITAL → REGULAÇÃO → TRANSFERÊNCIA"
            }
        else:  # NEGADA
            response_data = {
                "message": status_message,
                "protocolo": decisao.protocolo,
                "decisao": decisao.decisao_regulador,
                "justificativa": decisao.justificativa_negacao,
                "regulador": current_user.nome,
                "timestamp": datetime.utcnow().isoformat(),
                "fluxo": "HOSPITAL → REGULAÇÃO → VOLTA PARA HOSPITAL"
            }
        
        # Adicionar dados de auditoria
        response_data["auditoria"] = {
            "historico_id": historico.id,
            "decisao_ia_preservada": True,
            "decisao_regulador_registrada": True,
            "rastreabilidade_completa": True,
            "microservico": "MS-Regulacao"
        }
        
        logger.info(f"✅ Decisão registrada: {decisao.protocolo} - {tipo_decisao} por {current_user.email}")
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao registrar decisão: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.get("/estatisticas")
async def estatisticas_regulacao(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["REGULADOR", "ADMIN"]))
):
    """Estatísticas da regulação"""
    
    try:
        # Contar pacientes por status
        em_regulacao = db.query(PacienteRegulacao).filter(
            PacienteRegulacao.status == 'AGUARDANDO_REGULACAO'
        ).count()
        
        autorizadas = db.query(PacienteRegulacao).filter(
            PacienteRegulacao.status == 'INTERNACAO_AUTORIZADA'
        ).count()
        
        negadas = db.query(PacienteRegulacao).filter(
            PacienteRegulacao.status == 'REGULACAO_NEGADA'
        ).count()
        
        # Contar por classificação de risco
        criticos = db.query(PacienteRegulacao).filter(
            PacienteRegulacao.classificacao_risco == 'VERMELHO'
        ).count()
        
        # Tempo médio de processamento da IA
        decisoes_ia = db.query(HistoricoDecisoes).filter(
            HistoricoDecisoes.microservico_origem == 'MS-Regulacao'
        ).all()
        
        tempo_medio_ia = 0
        if decisoes_ia:
            tempos = [d.tempo_processamento for d in decisoes_ia if d.tempo_processamento]
            if tempos:
                tempo_medio_ia = sum(tempos) / len(tempos)
        
        return {
            "estatisticas": {
                "em_regulacao": em_regulacao,
                "autorizadas": autorizadas,
                "negadas": negadas,
                "criticos": criticos,
                "tempo_medio_ia_segundos": round(tempo_medio_ia, 2),
                "total_decisoes_ia": len(decisoes_ia)
            },
            "ia_status": {
                "biobert_disponivel": is_biobert_disponivel(),
                "pipeline_rag": True,
                "llm_suportados": ["ollama"]
            },
            "regulador": {
                "nome": current_user.nome,
                "tipo": current_user.tipo_usuario
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erro ao buscar estatísticas: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.post("/testar-biobert")
async def testar_biobert(
    texto_medico: str,
    current_user: Usuario = Depends(get_current_user)
):
    """Endpoint para testar BioBERT diretamente"""
    
    try:
        if not texto_medico or len(texto_medico.strip()) < 3:
            raise HTTPException(status_code=400, detail="Texto médico obrigatório")
        
        logger.info(f"🧬 Testando BioBERT para usuário: {current_user.email}")
        
        # Analisar com BioBERT
        resultado = extrair_entidades_biobert(texto_medico)
        
        return {
            "texto_analisado": texto_medico,
            "biobert_resultado": resultado,
            "biobert_disponivel": is_biobert_disponivel(),
            "testado_por": current_user.nome,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no teste BioBERT: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.post("/chamar-ambulancia")
async def chamar_ambulancia(
    protocolo: str,
    confirmar_chamada: bool = True,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["REGULADOR", "ADMIN"]))
):
    """
    Endpoint para acionar ambulância após decisão do regulador
    Integra com sistema de frota e gera alertas
    """
    
    try:
        # Buscar paciente e última decisão
        paciente = db.query(PacienteRegulacao).filter(
            PacienteRegulacao.protocolo == protocolo
        ).first()
        
        if not paciente:
            raise HTTPException(status_code=404, detail="Paciente não encontrado")
        
        # Buscar última decisão da IA com matchmaking
        ultima_decisao = db.query(HistoricoDecisoes).filter(
            HistoricoDecisoes.protocolo == protocolo
        ).order_by(HistoricoDecisoes.created_at.desc()).first()
        
        if not ultima_decisao:
            raise HTTPException(status_code=404, detail="Decisão da IA não encontrada")
        
        decisao_data = json.loads(ultima_decisao.decisao_ia)
        
        # Verificar se tem dados de matchmaking
        if "matchmaking_logistico" not in decisao_data:
            raise HTTPException(status_code=400, detail="Dados logísticos não disponíveis")
        
        matchmaking = decisao_data["matchmaking_logistico"]
        ambulancia = decisao_data.get("ambulancia_sugerida", {})
        rota = decisao_data.get("rota_otimizada", {})
        protocolo_especial = decisao_data.get("protocolo_especial", {})
        
        if confirmar_chamada:
            # Simular acionamento da ambulância (em produção seria API do SAMU)
            logger.info(f"🚑 AMBULÂNCIA ACIONADA: {ambulancia.get('id', 'N/A')} para protocolo {protocolo}")
            
            # Atualizar status do paciente
            paciente.status = "AMBULANCIA_ACIONADA"
            paciente.updated_at = datetime.utcnow()
            
            # Registrar acionamento no histórico
            historico_acionamento = HistoricoDecisoes(
                protocolo=protocolo,
                decisao_ia=json.dumps({
                    "acao": "AMBULANCIA_ACIONADA",
                    "ambulancia": ambulancia,
                    "rota": rota,
                    "acionado_por": {
                        "nome": current_user.nome,
                        "email": current_user.email
                    },
                    "timestamp": datetime.utcnow().isoformat()
                }),
                usuario_validador=current_user.email,
                tempo_processamento=0.0,
                microservico_origem="MS-Regulacao-Ambulancia"
            )
            db.add(historico_acionamento)
            db.commit()
            
            # Preparar alertas especiais
            alertas_especiais = []
            if protocolo_especial.get("ativo"):
                alertas_especiais = protocolo_especial.get("alertas", [])
                
                # Se for protocolo de óbito, enviar alertas específicos
                if protocolo_especial.get("tipo") == "PROTOCOLO_OBITO":
                    alertas_especiais.extend([
                        "🫀 CENTRAL DE TRANSPLANTES NOTIFICADA",
                        "👥 ASSISTÊNCIA SOCIAL ACIONADA",
                        "🏥 PROTOCOLO DE MANUTENÇÃO DE ÓRGÃOS ATIVO"
                    ])
            
            return {
                "message": "Ambulância acionada com sucesso",
                "protocolo": protocolo,
                "ambulancia_acionada": {
                    "id": ambulancia.get("id", "N/A"),
                    "tipo": ambulancia.get("tipo", "USB"),
                    "tempo_chegada_estimado": f"{ambulancia.get('tempo_chegada_min', 15)} minutos",
                    "regiao": ambulancia.get("regiao", "N/A")
                },
                "rota_confirmada": {
                    "hospital_destino": matchmaking.get("hospital_destino", "N/A"),
                    "distancia_km": matchmaking.get("distancia_km", 0),
                    "tempo_estimado": f"{matchmaking.get('tempo_estimado_min', 0)} minutos",
                    "via_recomendada": rota.get("via_recomendada", "Via urbana"),
                    "alertas_rota": rota.get("alertas_rota", [])
                },
                "protocolo_especial": {
                    "ativo": protocolo_especial.get("ativo", False),
                    "tipo": protocolo_especial.get("tipo", "NORMAL"),
                    "alertas_especiais": alertas_especiais,
                    "instrucoes": protocolo_especial.get("instrucoes", [])
                },
                "acionado_por": {
                    "regulador": current_user.nome,
                    "timestamp": datetime.utcnow().isoformat()
                },
                "auditoria": {
                    "historico_id": historico_acionamento.id,
                    "rastreabilidade_completa": True,
                    "microservico": "MS-Regulacao"
                }
            }
        else:
            # Apenas simular sem acionar
            return {
                "simulacao": True,
                "message": "Simulação de acionamento (não executado)",
                "dados_ambulancia": ambulancia,
                "dados_rota": matchmaking,
                "protocolo_especial": protocolo_especial
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao acionar ambulância: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)