"""Schemas Pydantic para Treinos."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class WorkoutCreate(BaseModel):
    exercise: str = Field(min_length=2, max_length=255)
    muscle_group: str = Field(min_length=2, max_length=100)
    sets: int = Field(gt=0, le=100)
    reps: int = Field(gt=0, le=1000)
    weight_kg: float = Field(ge=0, le=1000)
    rpe: Optional[int] = Field(None, ge=1, le=10)
    notes: Optional[str] = Field(None, max_length=1000)
    workout_date: datetime


class WorkoutUpdate(BaseModel):
    exercise: Optional[str] = Field(None, min_length=2, max_length=255)
    muscle_group: Optional[str] = Field(None, min_length=2, max_length=100)
    sets: Optional[int] = Field(None, gt=0, le=100)
    reps: Optional[int] = Field(None, gt=0, le=1000)
    weight_kg: Optional[float] = Field(None, ge=0, le=1000)
    rpe: Optional[int] = Field(None, ge=1, le=10)
    notes: Optional[str] = Field(None, max_length=1000)
    workout_date: Optional[datetime] = None


class WorkoutResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID
    user_id: UUID
    exercise: str
    muscle_group: str
    sets: int
    reps: int
    weight_kg: float
    rpe: Optional[int]
    notes: Optional[str]
    workout_date: datetime
    created_at: datetime


class WorkoutListResponse(BaseModel):
    items: List[WorkoutResponse]
    total: int
    page: int
    page_size: int
    pages: int
