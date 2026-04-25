"""Testes de log nutricional."""

import pytest
from datetime import date


@pytest.mark.asyncio
async def test_log_food(client, auth_headers):
    response = await client.post(
        "/api/v1/nutrition/log",
        headers=auth_headers,
        json={
            "food_name": "Frango Grelhado",
            "quantity_g": 150,
            "calories": 247,
            "protein_g": 46,
            "carbs_g": 0,
            "fat_g": 5.4,
            "log_date": str(date.today()),
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["food_name"] == "Frango Grelhado"
    assert data["calories"] == 247


@pytest.mark.asyncio
async def test_get_day_nutrition(client, auth_headers):
    today = str(date.today())
    # Registra um alimento
    await client.post(
        "/api/v1/nutrition/log",
        headers=auth_headers,
        json={
            "food_name": "Arroz",
            "quantity_g": 100,
            "calories": 130,
            "protein_g": 2.7,
            "carbs_g": 28,
            "fat_g": 0.3,
            "log_date": today,
        },
    )
    response = await client.get(f"/api/v1/nutrition/day/{today}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_calories" in data
    assert "items" in data
    assert len(data["items"]) >= 1
