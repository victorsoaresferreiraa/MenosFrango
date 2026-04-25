"""Repositório para operações de banco - Nutrição."""

from datetime import date
from typing import Optional
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.nutrition import NutritionLog


class NutritionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user_id: UUID, **kwargs) -> NutritionLog:
        log = NutritionLog(user_id=user_id, **kwargs)
        self.db.add(log)
        await self.db.flush()
        await self.db.refresh(log)
        return log

    async def get_by_date(self, user_id: UUID, log_date: date) -> list[NutritionLog]:
        result = await self.db.execute(
            select(NutritionLog).where(
                and_(NutritionLog.user_id == user_id, NutritionLog.log_date == log_date)
            )
        )
        return list(result.scalars().all())

    async def get_by_id(self, log_id: UUID, user_id: UUID) -> Optional[NutritionLog]:
        result = await self.db.execute(
            select(NutritionLog).where(
                and_(NutritionLog.id == log_id, NutritionLog.user_id == user_id)
            )
        )
        return result.scalar_one_or_none()

    async def delete(self, log: NutritionLog) -> None:
        await self.db.delete(log)
        await self.db.flush()
