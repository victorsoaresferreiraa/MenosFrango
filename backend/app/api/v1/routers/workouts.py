"""Router de Treinos: CRUD completo com paginação e filtros."""

import math
from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.repositories.workout import WorkoutRepository
from app.schemas.workout import WorkoutCreate, WorkoutListResponse, WorkoutResponse, WorkoutUpdate

router = APIRouter(prefix="/workouts", tags=["workouts"])


@router.get("", response_model=WorkoutListResponse)
async def list_workouts(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    muscle_group: Optional[str] = Query(default=None),
    date_from: Optional[datetime] = Query(default=None),
    date_to: Optional[datetime] = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Lista treinos do usuário com paginação e filtros."""
    repo = WorkoutRepository(db)
    items, total = await repo.get_list(
        user_id=current_user.id,
        page=page,
        page_size=page_size,
        muscle_group=muscle_group,
        date_from=date_from,
        date_to=date_to,
    )
    pages = math.ceil(total / page_size) if total > 0 else 1
    return WorkoutListResponse(items=items, total=total, page=page, page_size=page_size, pages=pages)


@router.post("", response_model=WorkoutResponse, status_code=status.HTTP_201_CREATED)
async def create_workout(
    data: WorkoutCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Cria novo registro de treino."""
    repo = WorkoutRepository(db)
    workout = await repo.create(user_id=current_user.id, **data.model_dump())
    return workout


@router.get("/{workout_id}", response_model=WorkoutResponse)
async def get_workout(
    workout_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Busca treino por ID."""
    repo = WorkoutRepository(db)
    workout = await repo.get_by_id(workout_id, current_user.id)
    if not workout:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Treino não encontrado")
    return workout


@router.put("/{workout_id}", response_model=WorkoutResponse)
async def update_workout(
    workout_id: UUID,
    data: WorkoutUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Atualiza treino."""
    repo = WorkoutRepository(db)
    workout = await repo.get_by_id(workout_id, current_user.id)
    if not workout:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Treino não encontrado")
    return await repo.update(workout, **data.model_dump(exclude_none=True))


@router.delete("/{workout_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workout(
    workout_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove treino."""
    repo = WorkoutRepository(db)
    workout = await repo.get_by_id(workout_id, current_user.id)
    if not workout:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Treino não encontrado")
    await repo.delete(workout)
