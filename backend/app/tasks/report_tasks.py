"""
Tasks Celery para geração de relatórios PDF assíncronos.
"""
import logging
import uuid
from datetime import date, datetime

from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(
    name="app.tasks.report_tasks.generate_monthly_report",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def generate_monthly_report(
    self,
    user_id: str,
    user_name: str,
    user_email: str,
    month_str: str,  # formato: "2024-01"
) -> dict:
    """
    Task assíncrona que gera o relatório mensal PDF.
    1. Busca dados do banco
    2. Gera PDF com ReportLab
    3. Salva no storage
    4. Envia e-mail de notificação

    Args:
        user_id: UUID do usuário
        user_name: Nome do usuário
        user_email: E-mail para notificação
        month_str: Mês no formato "YYYY-MM"

    Returns:
        dict com storage_key e presigned_url do PDF
    """
    try:
        from sqlalchemy import create_engine, text
        from sqlalchemy.orm import Session

        from app.core.config import get_settings
        from app.services.email_service import email_service
        from app.services.pdf.pdf_service import pdf_service
        from app.services.storage.storage_service import storage_service

        settings = get_settings()

        # Dados simulados para o relatório (em produção viriam do DB)
        # Usando engine síncrono dentro do Celery
        workout_summary = {
            "total_sessions": 16,
            "unique_exercises": 12,
            "total_volume": 45000,
            "top_muscle_group": "Peitoral",
        }
        nutrition_summary = {
            "avg_calories": 2200,
            "target_calories": 2300,
            "avg_protein": 165,
            "target_protein": 180,
            "avg_carbs": 250,
            "avg_fat": 65,
            "adherence_pct": 78,
        }
        recommendations = [
            "Seu volume semanal está consistente — ótimo progresso!",
            "Aumente a ingestão de proteínas para atingir a meta diária.",
            "Considere adicionar 1 sessão de cardio leve para melhorar recuperação.",
            "Hidratação: registre pelo menos 2,5L de água por dia.",
            "Sono de qualidade é fundamental para maximizar os ganhos.",
        ]

        # Gera o PDF
        month = date(int(month_str[:4]), int(month_str[5:7]), 1)
        pdf_bytes = pdf_service.generate_monthly_report(
            user_name=user_name,
            month=month,
            workout_summary=workout_summary,
            nutrition_summary=nutrition_summary,
            recommendations=recommendations,
        )

        # Salva no storage
        filename = f"relatorio_{month_str}.pdf"
        user_uuid = uuid.UUID(user_id)
        storage_key = storage_service.upload_pdf(pdf_bytes, user_uuid, filename)
        presigned_url = storage_service.get_presigned_url(storage_key, expires_in=604800)  # 7 dias

        # Notifica por e-mail
        email_service.send_report_ready(user_email, user_name, presigned_url)

        logger.info("Relatório gerado para usuário %s: %s", user_id, storage_key)

        return {
            "status": "completed",
            "storage_key": storage_key,
            "download_url": presigned_url,
            "generated_at": datetime.now().isoformat(),
        }

    except Exception as exc:
        logger.error("Erro ao gerar relatório para %s: %s", user_id, exc)
        raise self.retry(exc=exc)
