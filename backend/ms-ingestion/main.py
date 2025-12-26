from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import requests
import json
import logging
from typing import List, Dict
import sys
import os

# Adicionar o diretório pai ao path para importar shared
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared.database import get_db, PacienteRegulacao, create_tables

app = FastAPI(title="MS-Ingestion", description="Microserviço de Ingestão de Dados SES-GO")

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

class SESGoScraper:
    """Scraper otimizado para extrair dados da API CDA do painel Pentaho da SES-GO"""
    
    def __init__(self):
        self.cda_api_url = "https://indicadores.saude.go.gov.br/pentaho/plugin/cda/api/doQuery"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01'
        }
        self.cda_path = "/regulacao_transparencia/paineis/painel.cda"

    def _fetch_cda_data(self, data_access_id: str, params: Dict = None) -> Dict:
        """Busca dados da API CDA com tratamento de erro robusto"""
        query_params = {
            'path': self.cda_path,
            'dataAccessId': data_access_id,
            'outputIndexId': '1',
            'pageSize': '0',
            'pageStart': '0',
            'sortBy': ''
        }
        if params:
            query_params.update(params)
        
        try:
            response = requests.get(
                self.cda_api_url, 
                headers=self.headers, 
                params=query_params, 
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao buscar dados da API CDA para '{data_access_id}': {e}")
            return None

    def fetch_all_data(self) -> Dict[str, List]:
        """Busca todos os datasets necessários"""
        datasets = {
            'em_regulacao': 'dsLFElistaEmRegulacao',
            'admitidos': 'dsLFElistaAdmitidos', 
            'alta': 'dsLFElistaAlta',
            'em_transito': 'dsLFElistaEmTransito'
        }
        
        results = {}
        for key, dataset_id in datasets.items():
            logger.info(f"Buscando dados: {key}")
            data = self._fetch_cda_data(dataset_id)
            if data and 'resultset' in data:
                results[key] = data['resultset']
            else:
                results[key] = []
                logger.warning(f"Nenhum dado encontrado para {key}")
        
        return results

def parse_datetime(date_str: str) -> datetime:
    """Converte string de data para datetime"""
    try:
        return datetime.strptime(date_str, "%d/%m/%Y %H:%M:%S")
    except:
        try:
            return datetime.strptime(date_str, "%d/%m/%Y")
        except:
            return datetime.utcnow()

def sync_database_with_scraper_data(db: Session):
    """Sincroniza banco de dados com dados do scraper"""
    scraper = SESGoScraper()
    all_data = scraper.fetch_all_data()
    
    total_processed = 0
    
    for status, records in all_data.items():
        for record in records:
            try:
                # Mapear status
                status_map = {
                    'em_regulacao': 'EM_REGULACAO',
                    'admitidos': 'INTERNADA', 
                    'alta': 'COM_ALTA',
                    'em_transito': 'INTERNACAO_AUTORIZADA'
                }
                
                protocolo = record[1]
                
                # Verificar se já existe
                existing = db.query(PacienteRegulacao).filter(
                    PacienteRegulacao.protocolo == protocolo
                ).first()
                
                if existing:
                    # Atualizar status se mudou
                    new_status = status_map.get(status, 'DESCONHECIDO')
                    if existing.status != new_status:
                        existing.status = new_status
                        existing.updated_at = datetime.utcnow()
                        if len(record) > 11 and record[11]:  # unidade_destino
                            existing.unidade_destino = record[11]
                else:
                    # Criar novo registro
                    paciente = PacienteRegulacao(
                        protocolo=protocolo,
                        data_solicitacao=parse_datetime(record[2]),
                        status=status_map.get(status, 'DESCONHECIDO'),
                        tipo_leito=record[4] if len(record) > 4 else None,
                        especialidade=record[8] if len(record) > 8 else None,
                        cpf_mascarado=record[6] if len(record) > 6 else None,
                        codigo_procedimento=record[7] if len(record) > 7 else None,
                        unidade_solicitante=record[9] if len(record) > 9 else None,
                        cidade_origem=record[10] if len(record) > 10 else None,
                        unidade_destino=record[11] if len(record) > 11 else None,
                        data_atualizacao=parse_datetime(record[12]) if len(record) > 12 else datetime.utcnow(),
                        complexo_regulador=record[13] if len(record) > 13 else None
                    )
                    db.add(paciente)
                
                total_processed += 1
                
            except Exception as e:
                logger.error(f"Erro ao processar registro {record}: {e}")
                continue
    
    db.commit()
    logger.info(f"Sincronização concluída. {total_processed} registros processados.")
    return total_processed

@app.on_event("startup")
async def startup_event():
    """Criar tabelas na inicialização"""
    create_tables()
    logger.info("MS-Ingestion iniciado com sucesso")

@app.get("/")
async def root():
    return {"service": "MS-Ingestion", "status": "running", "version": "1.0.0"}

@app.post("/load-json-data")
async def load_json_data(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Carrega dados dos arquivos JSON para o banco de dados"""
    
    def load_data_task():
        try:
            # Importar o processador
            import sys
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from data_processor import SESGoDataProcessor
            
            # Processar dados
            data_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            processor = SESGoDataProcessor(data_dir)
            processed_data = processor.process_raw_data()
            
            total_loaded = 0
            
            # Mapear status
            status_map = {
                'em_regulacao': 'EM_REGULACAO',
                'admitidos': 'INTERNADA', 
                'alta': 'COM_ALTA',
                'em_transito': 'INTERNACAO_AUTORIZADA'
            }
            
            for status_key, df in processed_data.items():
                if df.empty:
                    continue
                
                for _, row in df.iterrows():
                    try:
                        protocolo = row.get('protocolo')
                        if not protocolo:
                            continue
                        
                        # Verificar se já existe
                        existing = db.query(PacienteRegulacao).filter(
                            PacienteRegulacao.protocolo == protocolo
                        ).first()
                        
                        if existing:
                            # Atualizar se necessário
                            new_status = status_map.get(status_key, 'DESCONHECIDO')
                            if existing.status != new_status:
                                existing.status = new_status
                                existing.updated_at = datetime.utcnow()
                        else:
                            # Criar novo registro
                            paciente = PacienteRegulacao(
                                protocolo=protocolo,
                                data_solicitacao=row.get('data_solicitacao_parsed', datetime.utcnow()),
                                status=status_map.get(status_key, 'DESCONHECIDO'),
                                tipo_leito=row.get('tipo_leito'),
                                especialidade=row.get('especialidade'),
                                cpf_mascarado=row.get('cpf_mascarado'),
                                codigo_procedimento=row.get('codigo_procedimento'),
                                unidade_solicitante=row.get('unidade_solicitante'),
                                cidade_origem=row.get('cidade_origem'),
                                unidade_destino=row.get('unidade_destino'),
                                complexo_regulador=row.get('complexo_regulador')
                            )
                            db.add(paciente)
                        
                        total_loaded += 1
                        
                        # Commit em lotes para performance
                        if total_loaded % 100 == 0:
                            db.commit()
                            
                    except Exception as e:
                        logger.error(f"Erro ao processar registro: {e}")
                        continue
            
            db.commit()
            logger.info(f"Carregamento concluído: {total_loaded} registros processados")
            
        except Exception as e:
            logger.error(f"Erro no carregamento de dados: {e}")
            db.rollback()
    
    background_tasks.add_task(load_data_task)
    return {"message": "Carregamento de dados JSON iniciado em background"}

@app.post("/sync")
async def trigger_sync(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Trigger manual da sincronização"""
    background_tasks.add_task(sync_database_with_scraper_data, db)
    return {"message": "Sincronização iniciada em background"}

@app.get("/pacientes")
async def get_pacientes(
    status: str = None,
    cidade: str = None,
    especialidade: str = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Endpoint para buscar pacientes com filtros"""
    query = db.query(PacienteRegulacao)
    
    if status:
        query = query.filter(PacienteRegulacao.status == status)
    if cidade:
        query = query.filter(PacienteRegulacao.cidade_origem.ilike(f"%{cidade}%"))
    if especialidade:
        query = query.filter(PacienteRegulacao.especialidade.ilike(f"%{especialidade}%"))
    
    pacientes = query.limit(limit).all()
    return pacientes

@app.get("/dashboard/leitos")
async def get_dashboard_leitos(db: Session = Depends(get_db)):
    """Endpoint otimizado para dashboard de leitos usando processador de dados"""
    
    try:
        # Primeiro tentar dados do banco
        status_counts = db.query(
            PacienteRegulacao.status,
            db.func.count(PacienteRegulacao.id).label('count')
        ).group_by(PacienteRegulacao.status).all()
        
        if status_counts:
            # Usar dados do banco se disponíveis
            unidade_counts = db.query(
                PacienteRegulacao.unidade_solicitante,
                PacienteRegulacao.cidade_origem,
                db.func.count(PacienteRegulacao.id).label('pacientes_em_fila')
            ).filter(
                PacienteRegulacao.status == 'EM_REGULACAO'
            ).group_by(
                PacienteRegulacao.unidade_solicitante,
                PacienteRegulacao.cidade_origem
            ).all()
            
            especialidade_counts = db.query(
                PacienteRegulacao.especialidade,
                db.func.count(PacienteRegulacao.id).label('count')
            ).filter(
                PacienteRegulacao.status == 'EM_REGULACAO'
            ).group_by(PacienteRegulacao.especialidade).all()
            
            return {
                "status_summary": [{"status": s.status, "count": s.count} for s in status_counts],
                "unidades_pressao": [
                    {
                        "unidade_executante_desc": u.unidade_solicitante,
                        "cidade": u.cidade_origem,
                        "pacientes_em_fila": u.pacientes_em_fila
                    } for u in unidade_counts
                ],
                "especialidades_demanda": [
                    {"especialidade": e.especialidade, "count": e.count} 
                    for e in especialidade_counts
                ],
                "ultima_atualizacao": datetime.utcnow().isoformat(),
                "fonte": "database"
            }
    except Exception as e:
        logger.warning(f"Erro ao buscar dados do banco: {e}")
    
    # Fallback: usar processador de dados dos arquivos JSON
    try:
        # Importar o processador
        import sys
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from data_processor import SESGoDataProcessor
        
        # Processar dados dos arquivos JSON (diretório raiz do projeto)
        data_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        processor = SESGoDataProcessor(data_dir)
        dashboard_data = processor.generate_dashboard_data()
        
        # Adicionar fonte dos dados
        dashboard_data["fonte"] = "json_files"
        
        logger.info(f"Dados carregados dos arquivos JSON: {dashboard_data.get('total_registros', 0)} registros")
        return dashboard_data
        
    except Exception as e:
        logger.error(f"Erro ao processar arquivos JSON: {e}")
        
        # Último fallback: dados simulados
        return {
            "status_summary": [
                {"status": "EM_REGULACAO", "count": 45},
                {"status": "INTERNADA", "count": 234},
                {"status": "COM_ALTA", "count": 89},
                {"status": "INTERNACAO_AUTORIZADA", "count": 12}
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
                }
            ],
            "especialidades_demanda": [
                {"especialidade": "CARDIOLOGIA", "count": 8},
                {"especialidade": "ORTOPEDIA", "count": 6},
                {"especialidade": "NEUROLOGIA", "count": 5}
            ],
            "ultima_atualizacao": datetime.utcnow().isoformat(),
            "fonte": "fallback_simulado"
        }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)