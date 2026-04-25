"""Repositório para operações de banco - Treinos."""

import math
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.workout import Workout


class WorkoutRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, workout_id: UUID, user_id: UUID) -> Optional[Workout]:
        result = await self.db.execute(
            select(Workout).where(
                and_(Workout.id == workout_id, Workout.user_id == user_id)
            )
        )
        return result.scalar_one_or_none()

    async def get_list(
        self,
        user_id: UUID,
        page: int = 1,
        page_size: int = 20,
        muscle_group: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> tuple[list[Workout], int]:
        """Retorna lista paginada e total de registros."""
        query = select(Workout).where(Workout.user_id == user_id)

        if muscle_group:
            query = query.where(Workout.muscle_group.ilike(f"%{muscle_group}%"))
        if date_from:
            query = query.where(Workout.workout_date >= date_from)
        if date_to:
            query = query.where(Workout.workout_date <= date_to)

        # Total
        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_query)).scalar_one()

        # Paginação
        offset = (page - 1) * page_size
        query = query.order_by(desc(Workout.workout_date)).offset(offset).limit(page_size)
        result = await self.db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def create(self, user_id: UUID, **kwargs) -> Workout:
        workout = Workout(user_id=user_id, **kwargs)
        self.db.add(workout)
        await self.db.flush()
        await self.db.refresh(workout)
        return workout

    async def update(self, workout: Workout, **kwargs) -> Workout:
        for key, value in kwargs.items():
            setattr(workout, key, value)
        await self.db.flush()
        await self.db.refresh(workout)
        return workout

    async def delete(self, workout: Workout) -> None:
        await self.db.delete(workout)
        await self.db.flush()

    async def get_recent(self, user_id: UUID, limit: int = 10) -> list[Workout]:
        result = await self.db.execute(
            select(Workout)
            .where(Workout.user_id == user_id)
            .order_by(desc(Workout.workout_date))
            .limit(limit)
        )
        return list(result.scalars().all())
