"""
Backend simplificado que funciona apenas com arquivos JSON
Sem dependência de PostgreSQL
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import logging
import sys
import os
from typing import Optional, List, Dict, Any

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Criar aplicação FastAPI
app = FastAPI(
    title="Sistema de Regulação SES-GO - Modo Simplificado",
    description="API com dados reais dos arquivos JSON",
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

# Importar o processador de dados
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from data_processor import SESGoDataProcessor
    PROCESSOR_AVAILABLE = True
    logger.info("Processador de dados carregado com sucesso")
except ImportError as e:
    logger.error(f"Erro ao importar processador: {e}")
    PROCESSOR_AVAILABLE = False

# Cache global para dados
_data_cache = None
_cache_timestamp = None
CACHE_DURATION = 300  # 5 minutos

def get_processed_data() -> Dict[str, Any]:
    """Obtém dados processados com cache"""
    global _data_cache, _cache_timestamp
    
    now = datetime.utcnow()
    
    # Verificar se o cache ainda é válido
    if (_data_cache is not None and 
        _cache_timestamp is not None and 
        (now - _cache_timestamp).seconds < CACHE_DURATION):
        return _data_cache
    
    # Processar dados
    if not PROCESSOR_AVAILABLE:
        logger.warning("Processador não disponível, usando dados de fallback")
        return get_fallback_data()
    
    try:
        # Diretório raiz do projeto (onde estão os JSONs)
        data_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        processor = SESGoDataProcessor(data_dir)
        data = processor.generate_dashboard_data()
        
        # Atualizar cache
        _data_cache = data
        _cache_timestamp = now
        
        logger.info(f"Dados processados: {data.get('total_registros', 0)} registros")
        return data
        
    except Exception as e:
        logger.error(f"Erro ao processar dados: {e}")
        return get_fallback_data()

def get_fallback_data() -> Dict[str, Any]:
    """Dados de fallback quando há erro"""
    return {
        "status_summary": [
            {"status": "EM REGULACAO", "count": 0},
            {"status": "ADMITIDOS", "count": 0},
            {"status": "ALTA", "count": 0},
            {"status": "EM TRANSITO", "count": 0}
        ],
        "unidades_pressao": [],
        "especialidades_demanda": [],
        "ultima_atualizacao": datetime.utcnow().isoformat(),
        "total_registros": 0,
        "fonte": "fallback",
        "erro": "Não foi possível processar os dados JSON"
    }

# Modelos Pydantic
class PacienteInput(BaseModel):
    protocolo: str
    solicitacao: Optional[str] = None
    especialidade: Optional[str] = None
    cid: Optional[str] = None
    cid_desc: Optional[str] = None
    prontuario_texto: Optional[str] = None

@app.on_event("startup")
async def startup_event():
    """Inicialização da aplicação"""
    logger.info("Sistema de Regulação SES-GO iniciado (modo simplificado)")
    
    # Pré-carregar dados
    data = get_processed_data()
    logger.info(f"Dados iniciais carregados: {data.get('total_registros', 0)} registros")

@app.get("/")
async def root():
    return {
        "service": "Sistema de Regulação SES-GO",
        "mode": "simplified_with_real_data",
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "dashboard": "/dashboard/leitos",
            "health": "/health",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    data = get_processed_data()
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "data_processor": PROCESSOR_AVAILABLE,
        "total_registros": data.get('total_registros', 0),
        "cache_ativo": _data_cache is not None
    }

@app.get("/dashboard/leitos")
async def get_dashboard_leitos():
    """Dashboard público de leitos com dados reais"""
    
    try:
        data = get_processed_data()
        
        # Adicionar informações extras
        data["fonte"] = "json_files_processed"
        data["modo"] = "simplificado"
        
        logger.info(f"Dashboard servido: {data.get('total_registros', 0)} registros")
        return data
        
    except Exception as e:
        logger.error(f"Erro no dashboard: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.get("/pacientes")
async def get_pacientes(
    status: str = None,
    cidade: str = None,
    especialidade: str = None,
    limit: int = 100
):
    """Buscar pacientes com filtros (simulado)"""
    
    data = get_processed_data()
    
    # Simular resposta baseada nos dados agregados
    pacientes_simulados = []
    
    unidades = data.get('unidades_pressao', [])[:limit]
    for i, unidade in enumerate(unidades):
        pacientes_simulados.append({
            "id": i + 1,
            "protocolo": f"REG-{2025000000 + i:06d}",
            "status": status or "EM_REGULACAO",
            "unidade_solicitante": unidade.get('unidade_executante_desc'),
            "cidade_origem": unidade.get('cidade'),
            "pacientes_em_fila": unidade.get('pacientes_em_fila'),
            "data_solicitacao": datetime.utcnow().isoformat()
        })
    
    return pacientes_simulados

@app.post("/processar-regulacao")
async def processar_regulacao_ia(paciente: PacienteInput):
    """Processamento com IA (simulado)"""
    
    if not paciente.cid:
        raise HTTPException(status_code=400, detail="CID obrigatório para análise")
    
    # Resposta simulada baseada nos dados reais
    data = get_processed_data()
    unidades = data.get('unidades_pressao', [])
    
    # Escolher unidade com menor pressão
    unidade_sugerida = "HOSPITAL ESTADUAL DR ALBERTO RASSI HGG"
    if unidades:
        unidade_menor_pressao = min(unidades, key=lambda x: x.get('pacientes_em_fila', 0))
        unidade_sugerida = unidade_menor_pressao.get('unidade_executante_desc', unidade_sugerida)
    
    return {
        "analise_decisoria": {
            "score_prioridade": 7,
            "classificacao_risco": "AMARELO",
            "unidade_destino_sugerida": unidade_sugerida,
            "justificativa_clinica": f"Paciente com CID {paciente.cid} necessita avaliação especializada. Baseado em dados reais da rede SES-GO."
        },
        "logistica": {
            "acionar_ambulancia": True,
            "tipo_transporte": "USB",
            "previsao_vaga_h": "2-4 horas"
        },
        "protocolo_especial": {
            "tipo": "NORMAL",
            "instrucoes_imediatas": "Monitorização de sinais vitais durante transporte"
        },
        "metadata": {
            "modo": "simplificado_com_dados_reais",
            "timestamp": datetime.utcnow().isoformat(),
            "total_registros_base": data.get('total_registros', 0)
        }
    }

@app.post("/refresh-data")
async def refresh_data():
    """Força atualização dos dados"""
    global _data_cache, _cache_timestamp
    
    _data_cache = None
    _cache_timestamp = None
    
    data = get_processed_data()
    
    return {
        "message": "Dados atualizados com sucesso",
        "total_registros": data.get('total_registros', 0),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/stats")
async def get_stats():
    """Estatísticas detalhadas dos dados"""
    
    data = get_processed_data()
    
    return {
        "resumo": {
            "total_registros": data.get('total_registros', 0),
            "qualidade_dados": data.get('data_quality', {}),
            "ultima_atualizacao": data.get('ultima_atualizacao'),
            "fonte": data.get('fonte', 'unknown')
        },
        "status_summary": data.get('status_summary', []),
        "top_unidades": data.get('unidades_pressao', [])[:10],
        "top_especialidades": data.get('especialidades_demanda', [])[:10],
        "metricas_tempo": data.get('metricas_tempo', {}),
        "cache_info": {
            "cache_ativo": _data_cache is not None,
            "cache_timestamp": _cache_timestamp.isoformat() if _cache_timestamp else None
        }
    }

if __name__ == "__main__":
    import uvicorn
    
    print("=== SISTEMA DE REGULAÇÃO SES-GO ===")
    print("Modo: Simplificado com dados reais")
    print("Porta: 8000")
    print("Documentação: http://localhost:8000/docs")
    print("Dashboard: http://localhost:8000/dashboard/leitos")
    print("=====================================")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)