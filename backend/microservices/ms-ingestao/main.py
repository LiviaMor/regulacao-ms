"""
MS-INGESTAO - Microserviço de Ingestão e Tendência
Responsável por: Memória de curto prazo do sistema, histórico de ocupação, cálculo de tendências
Atua como a "Memória de Curto Prazo" do ecossistema de regulação
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, Float, DateTime, desc
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import sys
import os
import logging

# Adicionar path para módulos compartilhados
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.database import get_db, Base, engine, SessionLocal, HistoricoOcupacao
from shared.auth import get_current_user, Usuario
from shared.utils import setup_logging

# Configurar logging
logger = setup_logging("MS-Ingestao")

# Criar tabela se não existir
Base.metadata.create_all(bind=engine)

# ============================================================================
# APLICAÇÃO FASTAPI
# ============================================================================

app = FastAPI(
    title="MS-Ingestao - Sistema de Regulação SES-GO",
    description="Microserviço de Ingestão de Dados e Cálculo de Tendências - Memória de Curto Prazo",
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

# ============================================================================
# MODELOS PYDANTIC
# ============================================================================

class OcupacaoInput(BaseModel):
    unidade_id: str
    unidade_nome: str
    tipo_leito: str
    ocupacao_percentual: float
    leitos_totais: int
    leitos_ocupados: int
    leitos_disponiveis: int
    fonte_dados: Optional[str] = "SCRAPER"

class OcupacaoBatchInput(BaseModel):
    registros: List[OcupacaoInput]

class HospitalTendencia(BaseModel):
    unidade_id: str
    unidade_nome: str
    tipo_leito: str
    ocupacao_atual: float
    tendencia: str  # ALTA, QUEDA, ESTAVEL
    variacao_percentual: float
    alerta_saturacao: bool
    previsao_saturacao_min: Optional[int] = None
    leitos_disponiveis: int
    ultima_atualizacao: datetime

# ============================================================================
# FUNÇÕES DE CÁLCULO DE TENDÊNCIA
# ============================================================================

def calcular_tendencia(historico_leitos: List[HistoricoOcupacao]) -> Dict[str, Any]:
    """
    Calcula tendência de ocupação baseado no histórico das últimas 6 horas
    
    Returns:
        Dict com tendência (ALTA, QUEDA, ESTAVEL), variação e previsão
    """
    if len(historico_leitos) < 2:
        return {
            "tendencia": "ESTAVEL",
            "variacao": 0.0,
            "previsao_saturacao_min": None,
            "dados_insuficientes": True
        }
    
    # Ordenar por data (mais antigo primeiro)
    historico_ordenado = sorted(historico_leitos, key=lambda x: x.data_coleta)
    
    # Pegar primeiro (6h atrás) e último (atual)
    primeira_leitura = historico_ordenado[0].ocupacao_percentual
    ultima_leitura = historico_ordenado[-1].ocupacao_percentual
    
    # Calcular variação
    variacao = ultima_leitura - primeira_leitura
    
    # Determinar tendência
    if variacao > 5:
        tendencia = "ALTA"
    elif variacao < -5:
        tendencia = "QUEDA"
    else:
        tendencia = "ESTAVEL"
    
    # Calcular previsão de saturação (se tendência de alta)
    previsao_saturacao_min = None
    if tendencia == "ALTA" and variacao > 0:
        # Calcular tempo até 100% baseado na taxa de variação
        tempo_historico_horas = 6  # Janela de 6 horas
        taxa_por_hora = variacao / tempo_historico_horas
        
        if taxa_por_hora > 0:
            percentual_restante = 100 - ultima_leitura
            horas_ate_saturacao = percentual_restante / taxa_por_hora
            previsao_saturacao_min = int(horas_ate_saturacao * 60)  # Converter para minutos
    
    return {
        "tendencia": tendencia,
        "variacao": round(variacao, 2),
        "previsao_saturacao_min": previsao_saturacao_min,
        "dados_insuficientes": False
    }


def gerar_alerta_saturacao(ocupacao_atual: float, tendencia: str) -> bool:
    """
    Gera alerta de saturação quando ocupação > 90% E tendência de ALTA
    """
    return ocupacao_atual > 90 and tendencia == "ALTA"


def gerar_mensagem_ia(hospital: Dict[str, Any]) -> str:
    """
    Gera mensagem enriquecida para o prompt do Llama/IA
    
    Antes: "O Hospital X tem 2 leitos vagos."
    Agora: "O Hospital X tem 2 leitos vagos, mas a tendência é de ocupação total 
           nos próximos 40 minutos devido ao aumento de demanda na região. 
           Considere o Hospital Y, que tem 3 leitos e tendência de queda."
    """
    nome = hospital.get("unidade_nome", "Hospital")
    leitos = hospital.get("leitos_disponiveis", 0)
    tendencia = hospital.get("tendencia", "ESTAVEL")
    previsao = hospital.get("previsao_saturacao_min")
    alerta = hospital.get("alerta_saturacao", False)
    ocupacao = hospital.get("ocupacao_atual", 0)
    
    # Mensagem base
    mensagem = f"{nome} tem {leitos} leitos vagos"
    
    # Adicionar contexto de tendência
    if tendencia == "ALTA":
        if previsao and previsao < 120:  # Menos de 2 horas
            mensagem += f", mas a tendência é de ocupação total nos próximos {previsao} minutos"
        else:
            mensagem += ", com tendência de ALTA na ocupação"
    elif tendencia == "QUEDA":
        mensagem += ", com tendência de QUEDA na ocupação (mais leitos disponíveis em breve)"
    else:
        mensagem += ", com ocupação estável"
    
    # Adicionar alerta se necessário
    if alerta:
        mensagem += ". ⚠️ ALERTA: Hospital próximo da saturação!"
    
    # Adicionar taxa de ocupação
    mensagem += f" (Ocupação atual: {ocupacao:.1f}%)"
    
    return mensagem

# ============================================================================
# ENDPOINTS
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Inicialização do microserviço"""
    logger.info("MS-Ingestao iniciado com sucesso - Memória de Curto Prazo ativa")

@app.get("/")
async def root():
    return {
        "service": "MS-Ingestao",
        "status": "running",
        "version": "1.0.0",
        "description": "Microserviço de Ingestão e Tendência - Memória de Curto Prazo"
    }

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    # Contar registros no histórico
    total_registros = db.query(HistoricoOcupacao).count()
    
    return {
        "service": "MS-Ingestao",
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "memoria_curto_prazo": {
            "total_registros": total_registros,
            "janela_analise": "6 horas"
        }
    }

@app.post("/ingerir-ocupacao")
async def ingerir_ocupacao(
    ocupacao: OcupacaoInput,
    db: Session = Depends(get_db)
):
    """Ingere um registro de ocupação no histórico"""
    
    try:
        novo_registro = HistoricoOcupacao(
            unidade_id=ocupacao.unidade_id,
            unidade_nome=ocupacao.unidade_nome,
            tipo_leito=ocupacao.tipo_leito,
            ocupacao_percentual=ocupacao.ocupacao_percentual,
            leitos_totais=ocupacao.leitos_totais,
            leitos_ocupados=ocupacao.leitos_ocupados,
            leitos_disponiveis=ocupacao.leitos_disponiveis,
            data_coleta=datetime.utcnow(),
            fonte_dados=ocupacao.fonte_dados
        )
        
        db.add(novo_registro)
        db.commit()
        db.refresh(novo_registro)
        
        logger.info(f"Ocupação ingerida: {ocupacao.unidade_id} - {ocupacao.ocupacao_percentual}%")
        
        return {
            "message": "Ocupação registrada com sucesso",
            "id": novo_registro.id,
            "unidade_id": ocupacao.unidade_id,
            "ocupacao": ocupacao.ocupacao_percentual,
            "timestamp": novo_registro.data_coleta.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erro ao ingerir ocupação: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao registrar ocupação: {str(e)}")

@app.post("/ingerir-ocupacao-batch")
async def ingerir_ocupacao_batch(
    batch: OcupacaoBatchInput,
    db: Session = Depends(get_db)
):
    """Ingere múltiplos registros de ocupação de uma vez"""
    
    try:
        registros_criados = []
        
        for ocupacao in batch.registros:
            novo_registro = HistoricoOcupacao(
                unidade_id=ocupacao.unidade_id,
                unidade_nome=ocupacao.unidade_nome,
                tipo_leito=ocupacao.tipo_leito,
                ocupacao_percentual=ocupacao.ocupacao_percentual,
                leitos_totais=ocupacao.leitos_totais,
                leitos_ocupados=ocupacao.leitos_ocupados,
                leitos_disponiveis=ocupacao.leitos_disponiveis,
                data_coleta=datetime.utcnow(),
                fonte_dados=ocupacao.fonte_dados
            )
            db.add(novo_registro)
            registros_criados.append(ocupacao.unidade_id)
        
        db.commit()
        
        logger.info(f"Batch ingerido: {len(registros_criados)} registros")
        
        return {
            "message": f"{len(registros_criados)} registros ingeridos com sucesso",
            "unidades": registros_criados,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erro ao ingerir batch: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao registrar batch: {str(e)}")


@app.get("/api/v1/inteligencia/hospitais-disponiveis")
async def get_hospitais_preditivo(
    especialidade: Optional[str] = None,
    tipo_leito: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Endpoint principal para a IA (Llama) - Retorna hospitais com dados enriquecidos de tendência
    
    Este endpoint é a "Memória de Curto Prazo" que alimenta o LLM com contexto preditivo:
    - Ocupação atual
    - Tendência (ALTA, QUEDA, ESTAVEL)
    - Alerta de saturação
    - Previsão de saturação em minutos
    - Mensagem formatada para o prompt do LLM
    """
    
    try:
        # Janela de análise: últimas 6 horas
        janela_inicio = datetime.utcnow() - timedelta(hours=6)
        
        # Buscar últimos registros de cada hospital do histórico
        from sqlalchemy import func
        
        # Subquery para pegar o último registro de cada hospital
        subquery = db.query(
            HistoricoOcupacao.unidade_id,
            func.max(HistoricoOcupacao.data_coleta).label('max_data')
        ).filter(
            HistoricoOcupacao.data_coleta >= janela_inicio
        ).group_by(HistoricoOcupacao.unidade_id).subquery()
        
        # Buscar registros mais recentes
        ultimos_registros = db.query(HistoricoOcupacao).join(
            subquery,
            (HistoricoOcupacao.unidade_id == subquery.c.unidade_id) &
            (HistoricoOcupacao.data_coleta == subquery.c.max_data)
        ).all()
        
        if not ultimos_registros:
            logger.warning("Nenhum dado de ocupação encontrado no histórico")
            return {
                "hospitais": [],
                "contexto_llm": {
                    "timestamp": datetime.utcnow().isoformat(),
                    "total_hospitais": 0,
                    "recomendacao_ia": "Sem dados de ocupação disponíveis. Execute /sincronizar-ocupacao no backend principal."
                },
                "metadata": {
                    "fonte": "MS-Ingestao",
                    "janela_analise": "6 horas",
                    "versao": "1.0.0",
                    "dados_disponiveis": False
                }
            }
        
        hospitais_enriquecidos = []
        
        for registro in ultimos_registros:
            unidade_id = registro.unidade_id
            
            # Buscar histórico completo das últimas 6 horas para tendência
            historico = db.query(HistoricoOcupacao).filter(
                HistoricoOcupacao.unidade_id == unidade_id,
                HistoricoOcupacao.data_coleta >= janela_inicio
            ).order_by(HistoricoOcupacao.data_coleta.asc()).limit(12).all()
            
            # Calcular tendência
            resultado_tendencia = calcular_tendencia(historico)
            
            # Gerar alerta de saturação
            ocupacao_atual = registro.ocupacao_percentual
            alerta = gerar_alerta_saturacao(ocupacao_atual, resultado_tendencia["tendencia"])
            
            # Status baseado na ocupação
            if ocupacao_atual >= 90:
                status = "CRITICO"
            elif ocupacao_atual >= 80:
                status = "ALTO"
            elif ocupacao_atual >= 70:
                status = "MODERADO"
            else:
                status = "NORMAL"
            
            # Montar dados enriquecidos
            hospital_enriquecido = {
                "hospital": registro.unidade_nome,
                "sigla": registro.unidade_id,
                "tipo_leito": registro.tipo_leito,
                "leitos_totais": registro.leitos_totais,
                "leitos_ocupados": registro.leitos_ocupados,
                "leitos_disponiveis": registro.leitos_disponiveis,
                "taxa_ocupacao": registro.ocupacao_percentual,
                "status_ocupacao": status,
                "ultima_atualizacao": registro.data_coleta.strftime("%H:%M"),
                "tendencia": resultado_tendencia["tendencia"],
                "variacao_6h": resultado_tendencia["variacao"],
                "previsao_saturacao_min": resultado_tendencia["previsao_saturacao_min"],
                "alerta_saturacao": alerta,
                "dados_tendencia_disponiveis": not resultado_tendencia.get("dados_insuficientes", True),
                "historico_pontos": len(historico),
                "fonte_dados": registro.fonte_dados
            }
            
            # Gerar mensagem para IA
            hospital_enriquecido["mensagem_ia"] = gerar_mensagem_ia(hospital_enriquecido)
            
            # Filtrar por especialidade se solicitado
            if especialidade:
                # Por enquanto, não filtramos por especialidade pois não temos esse dado no histórico
                pass
            
            # Filtrar por tipo de leito se solicitado
            if tipo_leito and registro.tipo_leito != tipo_leito:
                continue
            
            hospitais_enriquecidos.append(hospital_enriquecido)
        
        # Ordenar: Alertas primeiro, depois por disponibilidade
        hospitais_enriquecidos.sort(
            key=lambda x: (
                not x.get("alerta_saturacao", False),  # Alertas primeiro
                x.get("tendencia") != "QUEDA",  # Tendência de queda é melhor
                -x.get("leitos_disponiveis", 0)  # Mais leitos disponíveis
            )
        )
        
        # Gerar contexto completo para o LLM
        contexto_llm = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_hospitais": len(hospitais_enriquecidos),
            "hospitais_com_alerta": len([h for h in hospitais_enriquecidos if h.get("alerta_saturacao")]),
            "hospitais_tendencia_alta": len([h for h in hospitais_enriquecidos if h.get("tendencia") == "ALTA"]),
            "hospitais_tendencia_queda": len([h for h in hospitais_enriquecidos if h.get("tendencia") == "QUEDA"]),
            "recomendacao_ia": _gerar_recomendacao_geral(hospitais_enriquecidos)
        }
        
        return {
            "hospitais": hospitais_enriquecidos,
            "contexto_llm": contexto_llm,
            "metadata": {
                "fonte": "MS-Ingestao",
                "janela_analise": "6 horas",
                "versao": "1.0.0",
                "dados_disponiveis": True
            }
        }
        
    except Exception as e:
        logger.error(f"Erro ao buscar hospitais preditivos: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


def _gerar_recomendacao_geral(hospitais: List[Dict]) -> str:
    """Gera recomendação geral para o LLM baseado no estado atual do sistema"""
    
    alertas = [h for h in hospitais if h.get("alerta_saturacao")]
    tendencia_queda = [h for h in hospitais if h.get("tendencia") == "QUEDA"]
    
    if alertas:
        nomes_alerta = ", ".join([h.get("sigla", h.get("hospital", "")[:10]) for h in alertas[:3]])
        recomendacao = f"⚠️ ATENÇÃO: {len(alertas)} hospital(is) em alerta de saturação ({nomes_alerta}). "
        recomendacao += "Priorize hospitais com tendência de QUEDA ou ESTÁVEL para novos encaminhamentos."
    elif tendencia_queda:
        nomes_queda = ", ".join([h.get("sigla", h.get("hospital", "")[:10]) for h in tendencia_queda[:3]])
        recomendacao = f"✅ Sistema estável. Hospitais com tendência de QUEDA (mais vagas em breve): {nomes_queda}"
    else:
        recomendacao = "Sistema operando normalmente. Distribuição equilibrada de ocupação."
    
    return recomendacao


@app.get("/tendencia/{unidade_id}")
async def get_tendencia_hospital(
    unidade_id: str,
    tipo_leito: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Retorna tendência detalhada de um hospital específico"""
    
    try:
        # Janela de análise: últimas 6 horas
        janela_inicio = datetime.utcnow() - timedelta(hours=6)
        
        query = db.query(HistoricoOcupacao).filter(
            HistoricoOcupacao.unidade_id == unidade_id,
            HistoricoOcupacao.data_coleta >= janela_inicio
        )
        
        if tipo_leito:
            query = query.filter(HistoricoOcupacao.tipo_leito == tipo_leito)
        
        historico = query.order_by(HistoricoOcupacao.data_coleta.asc()).all()
        
        if not historico:
            return {
                "unidade_id": unidade_id,
                "tendencia": "DESCONHECIDA",
                "mensagem": "Sem dados históricos para análise",
                "dados_disponiveis": False
            }
        
        # Calcular tendência
        resultado = calcular_tendencia(historico)
        
        # Último registro
        ultimo = historico[-1] if historico else None
        
        return {
            "unidade_id": unidade_id,
            "unidade_nome": ultimo.unidade_nome if ultimo else "N/A",
            "tipo_leito": tipo_leito or "TODOS",
            "ocupacao_atual": ultimo.ocupacao_percentual if ultimo else 0,
            "leitos_disponiveis": ultimo.leitos_disponiveis if ultimo else 0,
            "tendencia": resultado["tendencia"],
            "variacao_6h": resultado["variacao"],
            "previsao_saturacao_min": resultado["previsao_saturacao_min"],
            "alerta_saturacao": gerar_alerta_saturacao(
                ultimo.ocupacao_percentual if ultimo else 0,
                resultado["tendencia"]
            ),
            "historico": [
                {
                    "data": h.data_coleta.isoformat(),
                    "ocupacao": h.ocupacao_percentual,
                    "leitos_disponiveis": h.leitos_disponiveis
                }
                for h in historico
            ],
            "dados_disponiveis": True
        }
        
    except Exception as e:
        logger.error(f"Erro ao buscar tendência: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@app.get("/historico/{unidade_id}")
async def get_historico_ocupacao(
    unidade_id: str,
    horas: int = 24,
    db: Session = Depends(get_db)
):
    """Retorna histórico de ocupação de um hospital"""
    
    try:
        janela_inicio = datetime.utcnow() - timedelta(hours=horas)
        
        historico = db.query(HistoricoOcupacao).filter(
            HistoricoOcupacao.unidade_id == unidade_id,
            HistoricoOcupacao.data_coleta >= janela_inicio
        ).order_by(HistoricoOcupacao.data_coleta.desc()).all()
        
        return {
            "unidade_id": unidade_id,
            "periodo_horas": horas,
            "total_registros": len(historico),
            "registros": [
                {
                    "id": h.id,
                    "data_coleta": h.data_coleta.isoformat(),
                    "ocupacao_percentual": h.ocupacao_percentual,
                    "leitos_totais": h.leitos_totais,
                    "leitos_ocupados": h.leitos_ocupados,
                    "leitos_disponiveis": h.leitos_disponiveis,
                    "tipo_leito": h.tipo_leito,
                    "fonte_dados": h.fonte_dados
                }
                for h in historico
            ]
        }
        
    except Exception as e:
        logger.error(f"Erro ao buscar histórico: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@app.delete("/limpar-historico-antigo")
async def limpar_historico_antigo(
    dias: int = 7,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Remove registros de histórico mais antigos que X dias (manutenção)"""
    
    try:
        data_limite = datetime.utcnow() - timedelta(days=dias)
        
        registros_deletados = db.query(HistoricoOcupacao).filter(
            HistoricoOcupacao.data_coleta < data_limite
        ).delete()
        
        db.commit()
        
        logger.info(f"Limpeza de histórico: {registros_deletados} registros removidos (>{dias} dias)")
        
        return {
            "message": f"{registros_deletados} registros removidos",
            "dias_mantidos": dias,
            "executado_por": current_user.email,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erro ao limpar histórico: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@app.get("/estatisticas")
async def get_estatisticas_ingestao(db: Session = Depends(get_db)):
    """Estatísticas do serviço de ingestão"""
    
    try:
        total_registros = db.query(HistoricoOcupacao).count()
        
        # Registros nas últimas 24h
        ultimas_24h = datetime.utcnow() - timedelta(hours=24)
        registros_24h = db.query(HistoricoOcupacao).filter(
            HistoricoOcupacao.data_coleta >= ultimas_24h
        ).count()
        
        # Unidades únicas
        unidades_unicas = db.query(HistoricoOcupacao.unidade_id).distinct().count()
        
        # Último registro
        ultimo_registro = db.query(HistoricoOcupacao).order_by(
            desc(HistoricoOcupacao.data_coleta)
        ).first()
        
        return {
            "estatisticas": {
                "total_registros": total_registros,
                "registros_ultimas_24h": registros_24h,
                "unidades_monitoradas": unidades_unicas,
                "ultimo_registro": ultimo_registro.data_coleta.isoformat() if ultimo_registro else None
            },
            "configuracao": {
                "janela_tendencia": "6 horas",
                "limiar_alta": "+5%",
                "limiar_queda": "-5%",
                "limiar_alerta_saturacao": "90%"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erro ao buscar estatísticas: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


# ============================================================================
# SIMULADOR DE DADOS (para desenvolvimento/testes)
# ============================================================================

@app.post("/simular-historico")
async def simular_historico(
    unidade_id: str,
    unidade_nome: str,
    horas: int = 6,
    db: Session = Depends(get_db)
):
    """
    Simula histórico de ocupação para testes
    Cria registros a cada 30 minutos nas últimas X horas
    """
    import random
    
    try:
        registros_criados = 0
        ocupacao_base = random.uniform(60, 85)
        
        for i in range(horas * 2):  # 2 registros por hora (a cada 30min)
            # Simular variação realística
            variacao = random.uniform(-3, 5)  # Tendência de alta leve
            ocupacao = max(40, min(98, ocupacao_base + variacao * (i / 2)))
            
            leitos_totais = 100
            leitos_ocupados = int(ocupacao)
            
            registro = HistoricoOcupacao(
                unidade_id=unidade_id,
                unidade_nome=unidade_nome,
                tipo_leito="GERAL",
                ocupacao_percentual=ocupacao,
                leitos_totais=leitos_totais,
                leitos_ocupados=leitos_ocupados,
                leitos_disponiveis=leitos_totais - leitos_ocupados,
                data_coleta=datetime.utcnow() - timedelta(minutes=30 * (horas * 2 - i)),
                fonte_dados="SIMULADOR"
            )
            db.add(registro)
            registros_criados += 1
        
        db.commit()
        
        return {
            "message": f"Histórico simulado criado com sucesso",
            "unidade_id": unidade_id,
            "registros_criados": registros_criados,
            "periodo_horas": horas
        }
        
    except Exception as e:
        logger.error(f"Erro ao simular histórico: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
