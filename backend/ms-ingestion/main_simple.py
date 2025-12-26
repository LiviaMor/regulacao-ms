from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import json
import os

app = FastAPI(title="MS-Ingestion (Modo Simples)", description="Microserviço de Ingestão - Versão Simplificada")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dados simulados para desenvolvimento
DADOS_SIMULADOS = {
    "status_summary": [
        {"status": "EM_REGULACAO", "count": 45},
        {"status": "INTERNACAO_AUTORIZADA", "count": 12},
        {"status": "INTERNADA", "count": 234},
        {"status": "COM_ALTA", "count": 89}
    ],
    "unidades_pressao": [
        {
            "unidade_executante_desc": "HOSPITAL ESTADUAL DR ALBERTO RASSI HGG",
            "cidade": "GOIANIA",
            "pacientes_em_fila": 18
        },
        {
            "unidade_executante_desc": "HOSPITAL DE URGENCIAS DE GOIAS DR VALDEMIRO CRUZ HUGO",
            "cidade": "GOIANIA", 
            "pacientes_em_fila": 15
        },
        {
            "unidade_executante_desc": "HOSPITAL ESTADUAL DE FORMOSA DR CESAR SAAD FAYAD",
            "cidade": "FORMOSA",
            "pacientes_em_fila": 12
        },
        {
            "unidade_executante_desc": "HOSPITAL MUNICIPAL DE MOZARLANDIA",
            "cidade": "MOZARLANDIA",
            "pacientes_em_fila": 8
        },
        {
            "unidade_executante_desc": "HOSPITAL ESTADUAL DO CENTRO NORTE GOIANO",
            "cidade": "URUACU",
            "pacientes_em_fila": 6
        }
    ],
    "especialidades_demanda": [
        {"especialidade": "ORTOPEDIA E TRAUMATOLOGIA", "count": 23},
        {"especialidade": "CLINICA MÉDICA", "count": 18},
        {"especialidade": "CARDIOLOGIA", "count": 12},
        {"especialidade": "CIRURGIA VASCULAR", "count": 8},
        {"especialidade": "NEUROLOGIA", "count": 5}
    ]
}

@app.get("/")
async def root():
    return {"service": "MS-Ingestion", "status": "running", "version": "1.0.0-simple"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.get("/dashboard/leitos")
async def get_dashboard_leitos():
    """Endpoint otimizado para dashboard de leitos"""
    return {
        **DADOS_SIMULADOS,
        "ultima_atualizacao": datetime.utcnow().isoformat()
    }

@app.get("/pacientes")
async def get_pacientes(status: str = None, limit: int = 10):
    """Endpoint para buscar pacientes"""
    # Dados simulados de pacientes
    pacientes_simulados = [
        {
            "protocolo": f"SIM-{i:04d}",
            "status": "EM_REGULACAO" if i % 3 == 0 else "INTERNADA",
            "especialidade": ["CARDIOLOGIA", "ORTOPEDIA", "CLINICA MÉDICA"][i % 3],
            "cidade_origem": ["GOIANIA", "ANAPOLIS", "FORMOSA"][i % 3],
            "data_solicitacao": datetime.utcnow().isoformat()
        }
        for i in range(1, limit + 1)
    ]
    
    if status:
        pacientes_simulados = [p for p in pacientes_simulados if p["status"] == status]
    
    return pacientes_simulados

@app.post("/sync")
async def trigger_sync():
    """Trigger manual da sincronização (simulado)"""
    return {"message": "Sincronização simulada executada com sucesso", "records_processed": 150}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)