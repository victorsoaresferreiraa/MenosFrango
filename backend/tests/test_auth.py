"""Testes de autenticação: register, login, refresh."""

import pytest


@pytest.mark.asyncio
async def test_register_success(client):
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "novo@test.com", "password": "senha123", "name": "Novo User"},
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_register_duplicate_email(client):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "dup@test.com", "password": "senha123", "name": "User"},
    )
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "dup@test.com", "password": "outrasenha", "name": "User 2"},
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_login_success(client):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "login@test.com", "password": "senha123", "name": "Login User"},
    )
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "login@test.com", "password": "senha123"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "wrong@test.com", "password": "certa", "name": "User"},
    )
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "wrong@test.com", "password": "errada"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_me(client, auth_headers):
    response = await client.get("/api/v1/users/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@test.com"


@pytest.mark.asyncio
async def test_get_me_unauthorized(client):
    response = await client.get("/api/v1/users/me")
    assert response.status_code == 403  # HTTPBearer retorna 403 sem header
