"""Router de Dashboard: KPIs e dados para gráficos."""

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func, select, text as sa_text
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.core.database import get_db
from app.models.nutrition import NutritionLog
from app.models.user import User
from app.models.workout import Workout
from app.repositories.workout import WorkoutRepository

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary")
async def get_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    now = datetime.now(timezone.utc)
    thirty_days_ago = now - timedelta(days=30)
    seven_days_ago  = now - timedelta(days=7)

    result = await db.execute(
        select(func.count(Workout.id)).where(
            Workout.user_id == current_user.id,
            Workout.workout_date >= thirty_days_ago,
        )
    )
    total_workouts_30d = result.scalar_one() or 0

    result = await db.execute(
        select(func.count(Workout.id)).where(
            Workout.user_id == current_user.id,
            Workout.workout_date >= seven_days_ago,
        )
    )
    total_workouts_7d = result.scalar_one() or 0

    result = await db.execute(
        select(func.sum(Workout.weight_kg * Workout.sets * Workout.reps)).where(
            Workout.user_id == current_user.id,
            Workout.workout_date >= thirty_days_ago,
        )
    )
    total_volume = result.scalar_one() or 0

    result = await db.execute(
        select(func.avg(NutritionLog.calories)).where(
            NutritionLog.user_id == current_user.id,
            NutritionLog.log_date >= seven_days_ago.date(),
        )
    )
    avg_calories = result.scalar_one() or 0

    repo = WorkoutRepository(db)
    recent = await repo.get_recent(current_user.id, limit=5)

    return {
        "user": {
            "name": current_user.name,
            "goal": current_user.goal,
            "level": current_user.level,
            "weight_kg": current_user.weight_kg,
        },
        "kpis": {
            "workouts_last_30d": total_workouts_30d,
            "workouts_last_7d": total_workouts_7d,
            "total_volume_last_30d_kg": round(float(total_volume), 1),
            "avg_daily_calories_7d": round(float(avg_calories), 0),
        },
        "recent_workouts": [
            {
                "id": str(w.id),
                "exercise": w.exercise,
                "muscle_group": w.muscle_group,
                "sets": w.sets,
                "reps": w.reps,
                "weight_kg": w.weight_kg,
                "workout_date": w.workout_date.isoformat(),
            }
            for w in recent
        ],
    }


@router.get("/graphs")
async def get_graphs(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    now = datetime.now(timezone.utc)
    since = now - timedelta(days=days)

    # Volume por grupo muscular
    result = await db.execute(
        select(
            Workout.muscle_group,
            func.sum(Workout.weight_kg * Workout.sets * Workout.reps).label("volume"),
            func.count(Workout.id).label("count"),
        )
        .where(Workout.user_id == current_user.id, Workout.workout_date >= since)
        .group_by(Workout.muscle_group)
        .order_by(func.sum(Workout.weight_kg * Workout.sets * Workout.reps).desc())
    )
    volume_by_group = [
        {"group": row.muscle_group, "volume": round(float(row.volume or 0), 1), "count": row.count}
        for row in result.all()
    ]

    # Evolução semanal — usa SQL literal para evitar bug do date_trunc com parâmetros
    result = await db.execute(
        sa_text("""
            SELECT
                date_trunc('week', workout_date) AS week,
                SUM(weight_kg * sets * reps)     AS volume,
                COUNT(id)                         AS workouts
            FROM workouts
            WHERE user_id = :uid AND workout_date >= :since
            GROUP BY date_trunc('week', workout_date)
            ORDER BY date_trunc('week', workout_date)
        """),
        {"uid": current_user.id, "since": since},
    )
    weekly_volume = [
        {
            "week": row.week.strftime("%d/%m") if row.week else "",
            "volume": round(float(row.volume or 0), 1),
            "workouts": row.workouts,
        }
        for row in result.all()
    ]

    # Calorias diárias
    result = await db.execute(
        select(
            NutritionLog.log_date,
            func.sum(NutritionLog.calories).label("calories"),
            func.sum(NutritionLog.protein_g).label("protein"),
        )
        .where(
            NutritionLog.user_id == current_user.id,
            NutritionLog.log_date >= since.date(),
        )
        .group_by(NutritionLog.log_date)
        .order_by(NutritionLog.log_date)
    )
    daily_calories = [
        {
            "date": row.log_date.strftime("%d/%m"),
            "calories": round(float(row.calories or 0), 0),
            "protein": round(float(row.protein or 0), 1),
        }
        for row in result.all()
    ]

    return {
        "volume_by_muscle_group": volume_by_group,
        "weekly_volume": weekly_volume,
        "daily_calories": daily_calories,
        "period_days": days,
    }
