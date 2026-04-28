"""
Configuração do Celery para tasks assíncronas.
Fallback: FastAPI BackgroundTasks quando Redis indisponível.
"""

from celery import Celery

from app.core.config import settings

# Instância do Celery
celery_app = Celery(
    "menosfrango",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.report_tasks"],
)

# Configurações
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Sao_Paulo",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    # Retry automático em caso de falha
    task_autoretry_for=(Exception,),
    task_retry_kwargs={"max_retries": 3, "countdown": 60},
)


@celery_app.task(bind=True, name="generate_monthly_report")
def generate_monthly_report_task(self, user_id: str, year: int, month: int) -> dict:
    """
    Task Celery para geração assíncrona do relatório mensal em PDF.
    """
    import asyncio
    from app.core.database import get_db_context

    async def _run():
        async with get_db_context() as db:
            from uuid import UUID
            from app.repositories.user import UserRepository
            from app.repositories.workout import WorkoutRepository
            from app.repositories.nutrition import NutritionRepository
            from app.services.pdf.report import generate_monthly_report
            from app.services.storage.s3 import storage_service
            from app.utils.email import send_email
            import calendar

            # Coleta dados
            user_repo = UserRepository(db)
            workout_repo = WorkoutRepository(db)
            nutrition_repo = NutritionRepository(db)

            user = await user_repo.get_by_id(UUID(user_id))
            if not user:
                return {"error": "Usuário não encontrado"}

            # Dados do mês
            from datetime import datetime, timezone
            date_from = datetime(year, month, 1, tzinfo=timezone.utc)
            last_day = calendar.monthrange(year, month)[1]
            date_to = datetime(year, month, last_day, 23, 59, 59, tzinfo=timezone.utc)

            workouts, _ = await workout_repo.get_list(
                user_id=UUID(user_id),
                page=1,
                page_size=1000,
                date_from=date_from,
                date_to=date_to,
            )

            # Calcular KPIs
            total_volume = sum(w.sets * w.reps * w.weight_kg for w in workouts)

            month_name = f"{calendar.month_name[month]} {year}"

            report_data = {
                "user": {
                    "name": user.name,
                    "goal": user.goal or "manutencao",
                    "level": user.level or "iniciante",
                    "weight_kg": user.weight_kg,
                },
                "month_name": month_name,
                "workouts": {
                    "total": len(workouts),
                    "total_sets": sum(w.sets for w in workouts),
                    "total_volume": total_volume,
                    "unique_exercises": len(set(w.exercise for w in workouts)),
                },
                "recommendations": [
                    "Continue com a progressão de cargas semanalmente.",
                    "Priorize descanso e sono de qualidade (7-9h).",
                    "Mantenha-se hidratado durante os treinos.",
                ],
            }

            # Gerar PDF
            pdf_bytes = generate_monthly_report(report_data)

            # Upload para storage
            key = f"reports/{user_id}/{year}/{month:02d}/relatorio.pdf"
            storage_service.client.put_object(
                Bucket=settings.S3_BUCKET,
                Key=key,
                Body=pdf_bytes,
                ContentType="application/pdf",
            )

            # Notificar usuário
            url = storage_service.get_public_url(key)
            send_email(
                user.email,
                f"Seu relatório de {month_name} está pronto!",
                f"<p>Olá, {user.name}!</p><p>Seu relatório mensal está disponível: <a href='{url}'>Download PDF</a></p>",
            )

            return {"status": "success", "key": key, "url": url}

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(_run())
    finally:
        loop.close()
