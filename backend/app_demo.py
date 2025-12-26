
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import json
import os

app = FastAPI(title="Sistema de Regulação SES-GO - Demo", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PacienteInput(BaseModel):
    protocolo: str
    especialidade: str = "CLINICA MÉDICA"
    cid: str = "Z00.0"
    cid_desc: str = "Exame médico geral"
    prontuario_texto: str = ""
    historico_paciente: str = ""
    prioridade_descricao: str = "Normal"

class LoginData(BaseModel):
    email: str
    senha: str

@app.get("/")
async def root():
    return {
        "service": "Sistema de Regulação SES-GO - Demo",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.get("/dashboard/leitos")
async def dashboard_leitos():
    return {
        "status_summary": [
            {"status": "EM_REGULACAO", "count": 25},
            {"status": "INTERNACAO_AUTORIZADA", "count": 8},
            {"status": "INTERNADA", "count": 156},
            {"status": "COM_ALTA", "count": 43}
        ],
        "unidades_pressao": [
            {
                "unidade_executante_desc": "HOSPITAL ESTADUAL DR ALBERTO RASSI HGG",
                "cidade": "GOIANIA",
                "pacientes_em_fila": 12
            },
            {
                "unidade_executante_desc": "HOSPITAL DE URGENCIAS DE GOIAS",
                "cidade": "GOIANIA", 
                "pacientes_em_fila": 8
            },
            {
                "unidade_executante_desc": "HOSPITAL ESTADUAL DE FORMOSA",
                "cidade": "FORMOSA",
                "pacientes_em_fila": 5
            }
        ],
        "ultima_atualizacao": datetime.utcnow().isoformat()
    }

@app.post("/processar-regulacao")
async def processar_regulacao(paciente: PacienteInput):
    # Simular processamento IA
    import time
    time.sleep(1)  # Simular tempo de processamento
    
    # Determinar risco baseado no CID
    risco = "VERDE"
    score = 3
    if "I21" in paciente.cid or "emergencia" in paciente.prioridade_descricao.lower():
        risco = "VERMELHO"
        score = 9
    elif "urgente" in paciente.prioridade_descricao.lower():
        risco = "AMARELO" 
        score = 6
    
    return {
        "analise_decisoria": {
            "score_prioridade": score,
            "classificacao_risco": risco,
            "unidade_destino_sugerida": "HOSPITAL ESTADUAL DR ALBERTO RASSI HGG",
            "justificativa_clinica": f"Paciente com {paciente.especialidade} - {paciente.cid_desc}. Análise baseada em protocolos padrão."
        },
        "logistica": {
            "acionar_ambulancia": risco in ["VERMELHO", "AMARELO"],
            "tipo_transporte": "USA" if risco == "VERMELHO" else "USB",
            "previsao_vaga_h": "1-2 horas" if risco == "VERMELHO" else "2-4 horas"
        },
        "protocolo_especial": {
            "tipo": "UTI" if risco == "VERMELHO" else "NORMAL",
            "instrucoes_imediatas": "Monitorização contínua" if risco == "VERMELHO" else "Cuidados padrão"
        },
        "metadata": {
            "tempo_processamento": 1.0,
            "biobert_usado": False,
            "timestamp": datetime.utcnow().isoformat()
        }
    }

@app.post("/login")
async def login(dados: LoginData):
    if dados.email == "admin@sesgo.gov.br" and dados.senha == "admin123":
        return {
            "access_token": "demo_token_12345",
            "token_type": "bearer",
            "user_info": {
                "id": 1,
                "email": dados.email,
                "nome": "Administrador Demo",
                "tipo_usuario": "ADMIN"
            }
        }
    raise HTTPException(status_code=401, detail="Credenciais inválidas")

@app.post("/transferencia")
async def transferencia(data: dict):
    return {
        "message": "Transferência autorizada com sucesso",
        "protocolo": data.get("protocolo"),
        "unidade_destino": data.get("unidade_destino"),
        "autorizado_por": "Administrador Demo"
    }

@app.get("/fila-regulacao")
async def fila_regulacao():
    return [
        {
            "protocolo": f"DEMO-{i:03d}",
            "data_solicitacao": datetime.utcnow().isoformat(),
            "especialidade": ["CARDIOLOGIA", "ORTOPEDIA", "NEUROLOGIA"][i % 3],
            "cidade_origem": ["GOIANIA", "ANAPOLIS", "FORMOSA"][i % 3],
            "unidade_solicitante": f"Hospital Municipal {i}",
            "score_prioridade": (i % 8) + 2,
            "classificacao_risco": ["VERDE", "AMARELO", "VERMELHO"][i % 3],
            "justificativa_tecnica": f"Paciente necessita avaliação em {['CARDIOLOGIA', 'ORTOPEDIA', 'NEUROLOGIA'][i % 3]}"
        }
        for i in range(1, 6)
    ]

@app.get("/dashboard-regulador")
async def dashboard_regulador():
    return {
        "estatisticas": {
            "em_regulacao": 25,
            "autorizadas": 8,
            "internadas": 156,
            "criticos": 3,
            "tempo_medio_regulacao_h": 1.8
        },
        "usuario": {
            "nome": "Administrador Demo",
            "tipo": "ADMIN"
        },
        "ultima_atualizacao": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
