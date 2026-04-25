"""
Schemas Pydantic para nutrição e fotos.
"""
import uuid
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


# ─── Nutrição ──────────────────────────────────────────────

class NutritionLogCreate(BaseModel):
    """Schema para registrar alimento."""

    food_name: str = Field(min_length=2, max_length=200)
    calories: float = Field(ge=0, le=10000)
    protein_g: float = Field(ge=0, le=1000)
    carbs_g: float = Field(ge=0, le=1000)
    fat_g: float = Field(ge=0, le=1000)
    quantity_g: float = Field(gt=0, le=10000, default=100.0)
    log_date: Optional[date] = None


class NutritionLogResponse(BaseModel):
    """Schema de resposta para registro nutricional."""

    model_config = {"from_attributes": True}

    id: uuid.UUID
    user_id: uuid.UUID
    food_name: str
    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float
    quantity_g: float
    log_date: date
    created_at: datetime


class NutritionDaySummary(BaseModel):
    """Totais nutricionais de um dia."""

    date: date
    total_calories: float
    total_protein_g: float
    total_carbs_g: float
    total_fat_g: float
    items: list[NutritionLogResponse]


# ─── Metas de macros ───────────────────────────────────────

class MacroTargets(BaseModel):
    """Metas diárias de macros calculadas pela IA/heurísticas."""

    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float
    tdee: float
    objetivo: str
    notes: str


# ─── Fotos corporais ───────────────────────────────────────

class PhotoCreate(BaseModel):
    """Metadados para upload de foto."""

    weight_kg: Optional[float] = Field(None, gt=0, lt=500)
    notes: Optional[str] = Field(None, max_length=500)
    photo_date: Optional[date] = None


class PhotoResponse(BaseModel):
    """Schema de resposta para foto corporal."""

    model_config = {"from_attributes": True}

    id: uuid.UUID
    user_id: uuid.UUID
    storage_key: str
    url: Optional[str] = None   # URL pré-assinada gerada em runtime
    weight_kg: Optional[float]
    notes: Optional[str]
    photo_date: date
    created_at: datetime
