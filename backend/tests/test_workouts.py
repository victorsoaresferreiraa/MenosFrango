"""Testes de CRUD de treinos."""

import pytest
from datetime import datetime, timezone


@pytest.mark.asyncio
async def test_create_workout(client, auth_headers):
    response = await client.post(
        "/api/v1/workouts",
        headers=auth_headers,
        json={
            "exercise": "Supino Reto",
            "muscle_group": "peito",
            "sets": 4,
            "reps": 10,
            "weight_kg": 80.0,
            "rpe": 8,
            "workout_date": datetime.now(timezone.utc).isoformat(),
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["exercise"] == "Supino Reto"
    assert data["muscle_group"] == "peito"
    assert data["weight_kg"] == 80.0


@pytest.mark.asyncio
async def test_list_workouts(client, auth_headers):
    # Cria um treino primeiro
    await client.post(
        "/api/v1/workouts",
        headers=auth_headers,
        json={
            "exercise": "Agachamento",
            "muscle_group": "quadriceps",
            "sets": 4,
            "reps": 8,
            "weight_kg": 100.0,
            "workout_date": datetime.now(timezone.utc).isoformat(),
        },
    )
    response = await client.get("/api/v1/workouts", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_delete_workout(client, auth_headers):
    # Cria
    create_resp = await client.post(
        "/api/v1/workouts",
        headers=auth_headers,
        json={
            "exercise": "Delete Test",
            "muscle_group": "peito",
            "sets": 3,
            "reps": 10,
            "weight_kg": 50.0,
            "workout_date": datetime.now(timezone.utc).isoformat(),
        },
    )
    workout_id = create_resp.json()["id"]

    # Deleta
    delete_resp = await client.delete(f"/api/v1/workouts/{workout_id}", headers=auth_headers)
    assert delete_resp.status_code == 204

    # Verifica que não existe mais
    get_resp = await client.get(f"/api/v1/workouts/{workout_id}", headers=auth_headers)
    assert get_resp.status_code == 404
