"""Schemas Pydantic para IA."""

from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class WorkoutPlanRequest(BaseModel):
    goal: str = Field(pattern="^(cutting|bulking|manutencao)$")
    weekly_frequency: int = Field(ge=2, le=7)
    level: str = Field(pattern="^(iniciante|intermediario|avancado)$")
    limitations: Optional[str] = None
    preferences: Optional[str] = None


class NutritionPlanRequest(BaseModel):
    weight_kg: float = Field(gt=0, le=500)
    height_cm: float = Field(gt=0, le=300)
    age: int = Field(gt=0, le=150)
    goal: str = Field(pattern="^(cutting|bulking|manutencao)$")
    activity_level: str = Field(
        default="moderado",
        pattern="^(sedentario|leve|moderado|ativo|muito_ativo)$"
    )


class ProgressAnalysisRequest(BaseModel):
    days: int = Field(default=30, ge=7, le=365)


class AIRecommendationResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID
    type: str
    payload: Dict[str, Any]
    ia_mode: str
    created_at: Any
