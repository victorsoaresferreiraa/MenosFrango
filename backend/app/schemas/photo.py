"""Schemas Pydantic para Fotos."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class PhotoResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID
    storage_key: str
    url: Optional[str] = None
    weight_kg: Optional[float]
    notes: Optional[str]
    taken_at: datetime
    created_at: datetime


class PhotoCreate(BaseModel):
    weight_kg: Optional[float] = Field(None, gt=0, le=500)
    notes: Optional[str] = Field(None, max_length=500)
    taken_at: Optional[datetime] = None
