"""Testes da camada de IA (Modo A - offline)."""

import pytest
import asyncio
from app.services.ai.offline import OfflineAIService


@pytest.mark.asyncio
async def test_workout_plan_generation():
    ai = OfflineAIService()
    result = await ai.generate_workout_plan({
        "goal": "bulking",
        "weekly_frequency": 4,
        "level": "intermediario",
    })
    assert result["ia_mode"] == "A"
    assert "days" in result
    assert len(result["days"]) > 0
    assert result["split"] is not None


@pytest.mark.asyncio
async def test_nutrition_plan_generation():
    ai = OfflineAIService()
    result = await ai.generate_nutrition_plan({
        "weight_kg": 80,
        "height_cm": 175,
        "age": 28,
        "goal": "cutting",
        "activity_level": "moderado",
    })
    assert result["ia_mode"] == "A"
    assert result["tdee"] > 0
    assert result["target_calories"] < result["tdee"]  # Cutting = déficit
    assert result["macros"]["protein_g"] > 0


@pytest.mark.asyncio
async def test_progress_analysis():
    ai = OfflineAIService()
    result = await ai.analyze_progress({
        "days": 30,
        "workouts": [
            {"muscle_group": "peito", "weight_kg": 80, "sets": 4, "reps": 10},
            {"muscle_group": "peito", "weight_kg": 82, "sets": 4, "reps": 10},
            {"muscle_group": "costas", "weight_kg": 70, "sets": 4, "reps": 10},
        ],
    })
    assert result["ia_mode"] == "A"
    assert len(result["insights"]) > 0
