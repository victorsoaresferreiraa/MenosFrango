"""Router admin — requer permissão is_admin."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentAdmin
from app.core.database import get_db
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserResponse

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/users", response_model=list[UserResponse])
async def list_users(
    admin: CurrentAdmin,
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = 0,
    limit: int = 50,
):
    """Lista todos os usuários (somente admin)."""
    repo = UserRepository(db)
    return await repo.list_all(skip=skip, limit=limit)


@router.get("/stats")
async def global_stats(
    admin: CurrentAdmin,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Estatísticas globais da plataforma."""
    from sqlalchemy import func, select
    from app.models.user import User
    from app.models.workout import Workout

    users_count = await db.execute(select(func.count()).select_from(User))
    workouts_count = await db.execute(select(func.count()).select_from(Workout))

    return {
        "total_usuarios": users_count.scalar_one(),
        "total_treinos": workouts_count.scalar_one(),
    }
