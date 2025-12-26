from celery import Celery
from celery.schedules import crontab
import os

# Configuração do Celery
celery_app = Celery(
    "regulacao_sesgo",
    broker=os.getenv("REDIS_URL", "redis://localhost:6379"),
    backend=os.getenv("REDIS_URL", "redis://localhost:6379"),
    include=["tasks"]
)

# Configurações
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Sao_Paulo",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutos
    task_soft_time_limit=25 * 60,  # 25 minutos
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Tarefas agendadas
celery_app.conf.beat_schedule = {
    # Sincronização automática a cada 10 minutos
    "sync-sesgo-data": {
        "task": "tasks.sync_sesgo_data",
        "schedule": crontab(minute="*/10"),
    },
    # Limpeza de logs antigos (diário às 2h)
    "cleanup-old-logs": {
        "task": "tasks.cleanup_old_logs", 
        "schedule": crontab(hour=2, minute=0),
    },
    # Relatório diário (às 8h)
    "daily-report": {
        "task": "tasks.generate_daily_report",
        "schedule": crontab(hour=8, minute=0),
    },
}

if __name__ == "__main__":
    celery_app.start()