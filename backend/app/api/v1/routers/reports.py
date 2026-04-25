"""Router de Relatórios: geração e download de PDF mensal."""

from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("/monthly")
async def request_monthly_report(
    year: int = None,
    month: int = None,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user: User = Depends(get_current_user),
):
    """Solicita geração do relatório mensal. Processado assincronamente."""
    now = datetime.now(timezone.utc)
    year = year or now.year
    month = month or now.month

    if not (1 <= month <= 12):
        raise HTTPException(status_code=400, detail="Mês inválido")

    # Tenta usar Celery; fallback para BackgroundTasks
    try:
        from app.tasks.celery_app import generate_monthly_report_task
        task = generate_monthly_report_task.delay(str(current_user.id), year, month)
        return {
            "status": "enqueued",
            "task_id": task.id,
            "message": f"Relatório de {month:02d}/{year} sendo gerado. Você receberá por e-mail.",
        }
    except Exception:
        # Fallback: BackgroundTask
        background_tasks.add_task(_generate_report_sync, str(current_user.id), year, month)
        return {
            "status": "processing",
            "message": f"Relatório de {month:02d}/{year} sendo gerado em background.",
        }


async def _generate_report_sync(user_id: str, year: int, month: int):
    """Fallback de geração de relatório sem Celery."""
    from app.core.database import get_db_context
    async with get_db_context() as db:
        from uuid import UUID
        from app.repositories.user import UserRepository
        from app.repositories.workout import WorkoutRepository
        from app.services.pdf.report import generate_monthly_report
        from app.services.storage.s3 import storage_service
        from app.utils.email import send_email
        import calendar
        from datetime import datetime, timezone

        repo = UserRepository(db)
        user = await repo.get_by_id(UUID(user_id))
        if not user:
            return

        workout_repo = WorkoutRepository(db)
        date_from = datetime(year, month, 1, tzinfo=timezone.utc)
        last_day = calendar.monthrange(year, month)[1]
        date_to = datetime(year, month, last_day, 23, 59, 59, tzinfo=timezone.utc)

        workouts, _ = await workout_repo.get_list(
            user_id=UUID(user_id), page=1, page_size=1000,
            date_from=date_from, date_to=date_to,
        )

        report_data = {
            "user": {
                "name": user.name, "goal": user.goal or "manutencao",
                "level": user.level or "iniciante", "weight_kg": user.weight_kg,
            },
            "month_name": f"{calendar.month_name[month]} {year}",
            "workouts": {
                "total": len(workouts),
                "total_sets": sum(w.sets for w in workouts),
                "total_volume": sum(w.sets * w.reps * w.weight_kg for w in workouts),
                "unique_exercises": len(set(w.exercise for w in workouts)),
            },
            "recommendations": ["Continue com o plano atual.", "Hidrate-se bem."],
        }

        pdf_bytes = generate_monthly_report(report_data)
        key = f"reports/{user_id}/{year}/{month:02d}/relatorio.pdf"

        try:
            storage_service.client.put_object(
                Bucket=storage_service.client.meta.endpoint_url and "athletic-bucket" or "athletic-bucket",
                Key=key, Body=pdf_bytes, ContentType="application/pdf",
            )
        except Exception:
            pass
