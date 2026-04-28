"""Schemas Pydantic para Nutrição."""

from datetime import date, datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class NutritionLogCreate(BaseModel):
    food_name: str = Field(min_length=2, max_length=255)
    quantity_g: float = Field(gt=0, le=10000)
    calories: float = Field(ge=0)
    protein_g: float = Field(ge=0, default=0.0)
    carbs_g: float = Field(ge=0, default=0.0)
    fat_g: float = Field(ge=0, default=0.0)
    log_date: date


class NutritionLogResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID
    food_name: str
    quantity_g: float
    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float
    log_date: date
    created_at: datetime


class NutritionDaySummary(BaseModel):
    log_date: date
    total_calories: float
    total_protein_g: float
    total_carbs_g: float
    total_fat_g: float
    items: List[NutritionLogResponse]


class MacroGoals(BaseModel):
    tdee: float
    target_calories: float
    protein_g: float
    carbs_g: float
    fat_g: float
    goal: str
