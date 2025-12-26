from celery import Celery
from datetime import datetime, timedelta
import logging
import sys
import os

# Adicionar o diretório pai ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from shared.database import SessionLocal, PacienteRegulacao, HistoricoDecisoes

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Instância do Celery
celery_app = Celery("regulacao_sesgo")

@celery_app.task(bind=True)
def sync_sesgo_data(self):
    """Tarefa para sincronizar dados do SES-GO"""
    try:
        from ms_ingestion.main import sync_database_with_scraper_data
        
        db = SessionLocal()
        total_processed = sync_database_with_scraper_data(db)
        db.close()
        
        logger.info(f"Sincronização automática concluída: {total_processed} registros")
        return {"status": "success", "records_processed": total_processed}
        
    except Exception as e:
        logger.error(f"Erro na sincronização automática: {e}")
        self.retry(countdown=300, max_retries=3)  # Retry em 5 minutos

@celery_app.task
def cleanup_old_logs(days_to_keep=30):
    """Limpar logs e dados antigos"""
    try:
        db = SessionLocal()
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        
        # Limpar histórico de decisões antigas
        deleted_count = db.query(HistoricoDecisoes).filter(
            HistoricoDecisoes.created_at < cutoff_date
        ).delete()
        
        db.commit()
        db.close()
        
        logger.info(f"Limpeza concluída: {deleted_count} registros removidos")
        return {"status": "success", "deleted_records": deleted_count}
        
    except Exception as e:
        logger.error(f"Erro na limpeza: {e}")
        return {"status": "error", "message": str(e)}

@celery_app.task
def generate_daily_report():
    """Gerar relatório diário"""
    try:
        db = SessionLocal()
        
        # Estatísticas do dia anterior
        yesterday = datetime.utcnow() - timedelta(days=1)
        start_of_day = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        # Contar regulações por status
        stats = {}
        for status in ["EM_REGULACAO", "INTERNACAO_AUTORIZADA", "INTERNADA", "COM_ALTA"]:
            count = db.query(PacienteRegulacao).filter(
                PacienteRegulacao.updated_at >= start_of_day,
                PacienteRegulacao.updated_at <= end_of_day,
                PacienteRegulacao.status == status
            ).count()
            stats[status] = count
        
        # Tempo médio de processamento
        decisoes = db.query(HistoricoDecisoes).filter(
            HistoricoDecisoes.created_at >= start_of_day,
            HistoricoDecisoes.created_at <= end_of_day
        ).all()
        
        tempo_medio = 0
        if decisoes:
            tempo_medio = sum(d.tempo_processamento for d in decisoes) / len(decisoes)
        
        db.close()
        
        report = {
            "date": yesterday.strftime("%Y-%m-%d"),
            "statistics": stats,
            "avg_processing_time": round(tempo_medio, 2),
            "total_decisions": len(decisoes)
        }
        
        logger.info(f"Relatório diário gerado: {report}")
        return report
        
    except Exception as e:
        logger.error(f"Erro ao gerar relatório: {e}")
        return {"status": "error", "message": str(e)}

@celery_app.task(bind=True)
def process_ai_analysis(self, patient_data):
    """Processar análise de IA de forma assíncrona"""
    try:
        from ms_intelligence.main import extrair_entidades_biobert, chamar_llama_docker
        
        # Simular processamento pesado
        extracao = extrair_entidades_biobert(patient_data.get("prontuario_texto", ""))
        
        # Montar prompt (versão simplificada)
        prompt = f"""
        Analise o paciente:
        - CID: {patient_data.get('cid')}
        - Especialidade: {patient_data.get('especialidade')}
        - Quadro: {extracao}
        
        Retorne JSON com score_prioridade (1-10) e classificacao_risco (VERDE/AMARELO/VERMELHO).
        """
        
        resultado = chamar_llama_docker(prompt)
        
        logger.info(f"Análise IA concluída para protocolo {patient_data.get('protocolo')}")
        return resultado
        
    except Exception as e:
        logger.error(f"Erro na análise IA: {e}")
        self.retry(countdown=60, max_retries=2)

@celery_app.task
def send_notification(user_id, message, notification_type="info"):
    """Enviar notificação para usuário"""
    try:
        # Implementar sistema de notificações (email, SMS, push)
        logger.info(f"Notificação enviada para usuário {user_id}: {message}")
        return {"status": "sent", "user_id": user_id, "type": notification_type}
        
    except Exception as e:
        logger.error(f"Erro ao enviar notificação: {e}")
        return {"status": "error", "message": str(e)}

@celery_app.task
def backup_database():
    """Fazer backup do banco de dados"""
    try:
        import subprocess
        
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_file = f"backup_regulacao_{timestamp}.sql"
        
        # Comando para backup (ajustar conforme ambiente)
        cmd = [
            "pg_dump",
            "-h", "localhost",
            "-U", "regulacao_user", 
            "-d", "regulacao_db",
            "-f", backup_file
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info(f"Backup criado: {backup_file}")
            return {"status": "success", "file": backup_file}
        else:
            logger.error(f"Erro no backup: {result.stderr}")
            return {"status": "error", "message": result.stderr}
            
    except Exception as e:
        logger.error(f"Erro ao fazer backup: {e}")
        return {"status": "error", "message": str(e)}