"""Router de Nutrição: log de refeições e resumos."""

from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.repositories.nutrition import NutritionRepository
from app.schemas.nutrition import MacroGoals, NutritionDaySummary, NutritionLogCreate, NutritionLogResponse

router = APIRouter(prefix="/nutrition", tags=["nutrition"])


@router.post("/log", response_model=NutritionLogResponse, status_code=status.HTTP_201_CREATED)
async def log_food(
    data: NutritionLogCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Registra ingestão de alimento."""
    repo = NutritionRepository(db)
    log = await repo.create(user_id=current_user.id, **data.model_dump())
    return log


@router.get("/day/{log_date}", response_model=NutritionDaySummary)
async def get_day_nutrition(
    log_date: date,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retorna todos os registros de nutrição de um dia com totais."""
    repo = NutritionRepository(db)
    items = await repo.get_by_date(current_user.id, log_date)

    totals = {
        "total_calories": sum(i.calories for i in items),
        "total_protein_g": sum(i.protein_g for i in items),
        "total_carbs_g": sum(i.carbs_g for i in items),
        "total_fat_g": sum(i.fat_g for i in items),
    }

    return NutritionDaySummary(log_date=log_date, items=items, **totals)


@router.get("/macro-goals", response_model=MacroGoals)
async def get_macro_goals(
    current_user: User = Depends(get_current_user),
):
    """Calcula e retorna metas de macros com base no perfil do usuário."""
    if not all([current_user.weight_kg, current_user.height_cm, current_user.age]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Atualize seu perfil com peso, altura e idade para calcular as metas.",
        )

    from app.services.ai.offline import OfflineAIService
    ai = OfflineAIService()
    result = await ai.generate_nutrition_plan({
        "weight_kg": current_user.weight_kg,
        "height_cm": current_user.height_cm,
        "age": current_user.age,
        "goal": current_user.goal or "manutencao",
        "activity_level": "moderado",
    })

    return MacroGoals(
        tdee=result["tdee"],
        target_calories=result["target_calories"],
        protein_g=result["macros"]["protein_g"],
        carbs_g=result["macros"]["carbs_g"],
        fat_g=result["macros"]["fat_g"],
        goal=result["goal"],
    )


@router.delete("/log/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_log(
    log_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove registro de nutrição."""
    repo = NutritionRepository(db)
    log = await repo.get_by_id(log_id, current_user.id)
    if not log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registro não encontrado")
    await repo.delete(log)
