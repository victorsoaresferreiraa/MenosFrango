"""
Tasks Celery para notificações e lembretes.
"""
import logging

from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.notification_tasks.send_weekly_reminder")
def send_weekly_reminder() -> dict:
    """
    Envia lembrete semanal de treino para usuários ativos.
    Agendado toda segunda-feira às 08:00.
    """
    logger.info("Iniciando envio de lembretes semanais...")
    # Em produção: busca usuários ativos do DB e envia e-mail
    # Por ora, apenas loga
    logger.info("Lembretes semanais enviados (dev: log)")
    return {"status": "completed", "sent_count": 0}
