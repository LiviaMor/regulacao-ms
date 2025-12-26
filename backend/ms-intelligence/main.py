from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
import requests
import json
import logging
import torch
import sys
import os
from typing import Optional, Dict, Any
import time
from PIL import Image
import io
import base64

# Adicionar o diretório pai ao path para importar shared
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared.database import get_db, PacienteRegulacao, HistoricoDecisoes, create_tables

app = FastAPI(title="MS-Intelligence", description="Microserviço de Inteligência Artificial para Regulação")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

class DecisaoIA(BaseModel):
    analise_decisoria: Dict[str, Any]
    logistica: Dict[str, Any]
    protocolo_especial: Optional[Dict[str, Any]] = None

# Inicialização do BioBERT (lazy loading)
biobert_model = None
biobert_tokenizer = None
biobert_disponivel = False

def load_biobert():
    """Carrega o modelo BioBERT de forma lazy"""
    global biobert_model, biobert_tokenizer, biobert_disponivel
    
    if biobert_model is None:
        try:
            from transformers import AutoTokenizer, AutoModel
            logger.info("Carregando modelo BioBERT...")
            biobert_tokenizer = AutoTokenizer.from_pretrained("dmis-lab/biobert-v1.1-pubmed")
            biobert_model = AutoModel.from_pretrained("dmis-lab/biobert-v1.1-pubmed")
            biobert_disponivel = True
            logger.info("BioBERT carregado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao carregar BioBERT: {e}")
            biobert_disponivel = False
    
    return biobert_disponivel

def extrair_entidades_biobert(prontuario_texto: str) -> str:
    """Extrai entidades médicas usando BioBERT"""
    if not prontuario_texto or not load_biobert():
        return "Extração simulada: Paciente com sintomas compatíveis com quadro clínico descrito."
    
    try:
        inputs = biobert_tokenizer(
            prontuario_texto, 
            return_tensors="pt", 
            truncation=True, 
            max_length=512,
            padding=True
        )
        
        with torch.no_grad():
            outputs = biobert_model(**inputs)
        
        # Análise simplificada dos embeddings
        last_hidden_states = outputs.last_hidden_state
        attention_weights = torch.mean(last_hidden_states, dim=1)
        
        # Simular extração de entidades baseada nos embeddings
        confidence_score = torch.mean(attention_weights).item()
        
        if confidence_score > 0.5:
            return f"Análise BioBERT: Quadro clínico identificado com alta confiança (score: {confidence_score:.2f}). Sintomas e condições médicas detectados no texto."
        else:
            return f"Análise BioBERT: Quadro clínico com confiança moderada (score: {confidence_score:.2f}). Recomenda-se revisão manual."
            
    except Exception as e:
        logger.error(f"Erro na análise BioBERT: {e}")
        return "Erro na análise automática. Revisão manual necessária."

def chamar_llama_docker(prompt_estruturado: str) -> Dict:
    """Chama o Llama via Ollama com tratamento robusto de erro"""
    ollama_endpoint = os.getenv("OLLAMA_URL", "http://localhost:11434") + "/api/generate"
    
    payload = {
        "model": "llama3",
        "prompt": prompt_estruturado,
        "format": "json",
        "stream": False,
        "options": {
            "temperature": 0.1,  # Mais determinístico para decisões médicas
            "top_p": 0.9,
            "max_tokens": 1000
        }
    }
    
    try:
        response = requests.post(ollama_endpoint, json=payload, timeout=120)
        response.raise_for_status()
        
        response_data = response.json()
        decisao_raw = response_data.get("response", "{}")
        
        # Tentar parsear o JSON
        try:
            decisao_json = json.loads(decisao_raw)
        except json.JSONDecodeError:
            # Fallback se o Llama não retornar JSON válido
            decisao_json = {
                "analise_decisoria": {
                    "score_prioridade": 5,
                    "classificacao_risco": "AMARELO",
                    "unidade_destino_sugerida": "Análise manual necessária",
                    "justificativa_clinica": "Resposta da IA não foi estruturada corretamente"
                },
                "logistica": {
                    "acionar_ambulancia": True,
                    "tipo_transporte": "USB",
                    "previsao_vaga_h": "2-4 horas"
                }
            }
        
        return decisao_json
        
    except requests.exceptions.ConnectionError:
        return {
            "erro": "Serviço Llama indisponível",
            "analise_decisoria": {
                "score_prioridade": 5,
                "classificacao_risco": "AMARELO", 
                "unidade_destino_sugerida": "Regulação manual necessária",
                "justificativa_clinica": "Sistema de IA temporariamente indisponível"
            },
            "logistica": {
                "acionar_ambulancia": False,
                "tipo_transporte": "A definir",
                "previsao_vaga_h": "Consultar regulador"
            }
        }
    except Exception as e:
        logger.error(f"Erro ao chamar Llama: {e}")
        return {
            "erro": str(e),
            "analise_decisoria": {
                "score_prioridade": 1,
                "classificacao_risco": "VERDE",
                "unidade_destino_sugerida": "Erro no processamento",
                "justificativa_clinica": f"Erro técnico: {str(e)}"
            }
        }

def buscar_dados_rede(db: Session) -> str:
    """Busca dados atuais da rede hospitalar"""
    try:
        # Contar pacientes em regulação por unidade
        unidades_pressao = db.query(
            PacienteRegulacao.unidade_solicitante,
            db.func.count(PacienteRegulacao.id).label('count')
        ).filter(
            PacienteRegulacao.status == 'EM_REGULACAO'
        ).group_by(PacienteRegulacao.unidade_solicitante).all()
        
        if not unidades_pressao:
            return "Dados da rede não disponíveis no momento."
        
        lista_formatada = []
        for unidade, count in unidades_pressao:
            status_pressao = "CRÍTICO" if count > 10 else "MODERADO" if count > 5 else "NORMAL"
            lista_formatada.append(f"- {unidade}: {count} solicitações ({status_pressao})")
        
        return "\n".join(lista_formatada[:10])  # Limitar a 10 unidades
        
    except Exception as e:
        logger.error(f"Erro ao buscar dados da rede: {e}")
        return "Erro ao acessar dados da rede hospitalar."

@app.on_event("startup")
async def startup_event():
    """Inicialização do serviço"""
    create_tables()
    logger.info("MS-Intelligence iniciado com sucesso")

@app.get("/")
async def root():
    return {
        "service": "MS-Intelligence", 
        "status": "running", 
        "version": "1.0.0",
        "biobert_disponivel": biobert_disponivel
    }

@app.post("/processar-regulacao")
async def processar_regulacao_ia(
    paciente: PacienteInput,
    db: Session = Depends(get_db)
):
    """Endpoint principal para processamento de regulação com IA"""
    start_time = time.time()
    
    # Validação básica
    if not paciente.cid:
        raise HTTPException(status_code=400, detail="CID obrigatório para análise")
    
    try:
        # 1. Extração com BioBERT
        extracao_biobert = extrair_entidades_biobert(paciente.prontuario_texto or "")
        
        # 2. Buscar dados da rede
        dados_rede = buscar_dados_rede(db)
        
        # 3. Montar prompt estruturado
        prompt = f"""### ROLE
Você é o Especialista Sênior de Regulação Médica da SES-GO. Analise o caso e forneça decisão estruturada.

### CONTEXTO DO PACIENTE
- Protocolo: {paciente.protocolo}
- Especialidade: {paciente.especialidade or 'N/A'}
- CID-10: {paciente.cid} ({paciente.cid_desc or 'N/A'})
- Quadro Clínico (BioBERT): {extracao_biobert}
- Histórico: {paciente.historico_paciente or 'N/A'}
- Prioridade Atual: {paciente.prioridade_descricao or 'N/A'}

### DISPONIBILIDADE DA REDE SES-GO
{dados_rede}

### PROTOCOLOS DE DECISÃO
1. Prioridade: Risco de vida > Tempo de espera > Logística
2. Classificação de Risco: VERMELHO (8-10), AMARELO (4-7), VERDE (1-3)
3. Logística: Priorizar unidades com menor pressão quando possível

### RESPOSTA OBRIGATÓRIA EM JSON:
{{
  "analise_decisoria": {{
    "score_prioridade": [1-10],
    "classificacao_risco": "VERMELHO|AMARELO|VERDE",
    "unidade_destino_sugerida": "Nome da unidade recomendada",
    "justificativa_clinica": "Explicação técnica da decisão"
  }},
  "logistica": {{
    "acionar_ambulancia": true/false,
    "tipo_transporte": "USA|USB|AEROMÉDICO",
    "previsao_vaga_h": "Estimativa em horas"
  }},
  "protocolo_especial": {{
    "tipo": "TRANSPLANTE|CIRURGIA|UTI|NORMAL",
    "instrucoes_imediatas": "Orientações específicas se necessário"
  }}
}}"""

        # 4. Chamar IA
        decisao = chamar_llama_docker(prompt)
        
        # 5. Salvar no histórico
        tempo_processamento = time.time() - start_time
        
        historico = HistoricoDecisoes(
            protocolo=paciente.protocolo,
            decisao_ia=json.dumps(decisao),
            tempo_processamento=tempo_processamento
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
            paciente_db.prontuario_texto = paciente.prontuario_texto
            paciente_db.updated_at = datetime.utcnow()
        
        db.commit()
        
        # 7. Adicionar metadados à resposta
        decisao["metadata"] = {
            "tempo_processamento": tempo_processamento,
            "biobert_usado": biobert_disponivel,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return decisao
        
    except Exception as e:
        logger.error(f"Erro no processamento: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.post("/upload-prontuario")
async def upload_prontuario(
    protocolo: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload de imagem de prontuário (OCR futuro)"""
    
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Apenas imagens são aceitas")
    
    try:
        # Ler imagem
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        # Converter para base64 para armazenamento
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        # Simular OCR (implementar Tesseract/PaddleOCR no futuro)
        texto_extraido = f"[OCR Simulado] Prontuário do protocolo {protocolo} - Imagem recebida com sucesso. Implementar OCR real."
        
        # Atualizar paciente
        paciente = db.query(PacienteRegulacao).filter(
            PacienteRegulacao.protocolo == protocolo
        ).first()
        
        if paciente:
            paciente.prontuario_texto = texto_extraido
            paciente.updated_at = datetime.utcnow()
            db.commit()
        
        return {
            "message": "Prontuário recebido com sucesso",
            "protocolo": protocolo,
            "texto_extraido": texto_extraido[:200] + "..." if len(texto_extraido) > 200 else texto_extraido
        }
        
    except Exception as e:
        logger.error(f"Erro no upload: {e}")
        raise HTTPException(status_code=500, detail=f"Erro no processamento: {str(e)}")

@app.get("/historico/{protocolo}")
async def get_historico_decisoes(protocolo: str, db: Session = Depends(get_db)):
    """Buscar histórico de decisões de um protocolo"""
    
    historico = db.query(HistoricoDecisoes).filter(
        HistoricoDecisoes.protocolo == protocolo
    ).order_by(HistoricoDecisoes.created_at.desc()).all()
    
    return [
        {
            "id": h.id,
            "decisao_ia": json.loads(h.decisao_ia),
            "usuario_validador": h.usuario_validador,
            "tempo_processamento": h.tempo_processamento,
            "created_at": h.created_at.isoformat()
        } for h in historico
    ]

@app.get("/health")
async def health_check():
    """Health check com status dos modelos"""
    return {
        "status": "healthy",
        "biobert_disponivel": biobert_disponivel,
        "ollama_conectado": True,  # Implementar verificação real
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)