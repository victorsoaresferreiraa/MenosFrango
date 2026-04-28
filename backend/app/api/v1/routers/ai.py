"""Router de IA: geração de planos e análise de progresso."""

from fastapi import APIRouter, Depends
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.core.database import get_db
from app.models.ai_recommendation import AIRecommendation
from app.models.user import User
from app.schemas.ai import (
    AIRecommendationResponse,
    NutritionPlanRequest,
    ProgressAnalysisRequest,
    WorkoutPlanRequest,
)
from app.services.ai.base import get_ai_service

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/workout-plan", response_model=AIRecommendationResponse)
async def generate_workout_plan(
    data: WorkoutPlanRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Gera plano de treino semanal via IA."""
    ai = get_ai_service()
    result = await ai.generate_workout_plan(data.model_dump())

    # BUGFIX: campo é 'payload' no modelo, não confundir com a variável 'payload'
    rec = AIRecommendation(
        user_id=current_user.id,
        type="workout_plan",
        payload=result,
        ia_mode=result.get("ia_mode", "A"),
    )
    db.add(rec)
    await db.flush()
    await db.refresh(rec)
    return rec


@router.post("/nutrition-plan", response_model=AIRecommendationResponse)
async def generate_nutrition_plan(
    data: NutritionPlanRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Gera plano nutricional via IA."""
    ai = get_ai_service()
    result = await ai.generate_nutrition_plan(data.model_dump())

    rec = AIRecommendation(
        user_id=current_user.id,
        type="nutrition_plan",
        payload=result,
        ia_mode=result.get("ia_mode", "A"),
    )
    db.add(rec)
    await db.flush()
    await db.refresh(rec)
    return rec


@router.post("/analyze-progress", response_model=AIRecommendationResponse)
async def analyze_progress(
    data: ProgressAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Analisa progresso do usuário nos últimos N dias."""
    from datetime import datetime, timedelta, timezone

    now = datetime.now(timezone.utc)
    since = now - timedelta(days=data.days)

    from app.models.workout import Workout

    result = await db.execute(
        select(Workout).where(
            Workout.user_id == current_user.id,
            Workout.workout_date >= since,
        )
    )
    workouts = [
        {
            "muscle_group": w.muscle_group,
            "weight_kg": w.weight_kg,
            "sets": w.sets,
            "reps": w.reps,
        }
        for w in result.scalars().all()
    ]

    ai = get_ai_service()
    analysis = await ai.analyze_progress({"days": data.days, "workouts": workouts})

    rec = AIRecommendation(
        user_id=current_user.id,
        type="progress_analysis",
        payload=analysis,
        ia_mode=analysis.get("ia_mode", "A"),
    )
    db.add(rec)
    await db.flush()
    await db.refresh(rec)
    return rec


@router.get("/history", response_model=list[AIRecommendationResponse])
async def get_ai_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retorna histórico de recomendações da IA."""
    result = await db.execute(
        select(AIRecommendation)
        .where(AIRecommendation.user_id == current_user.id)
        .order_by(desc(AIRecommendation.created_at))
        .limit(20)
    )
    return list(result.scalars().all())