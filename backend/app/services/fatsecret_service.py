import base64
import time
from typing import Any

import httpx
from fastapi import HTTPException

from app.core.config import settings


_token_cache = {
    "access_token": None,
    "expires_at": 0,
}


async def get_fatsecret_token() -> str:
    now = int(time.time())

    if _token_cache["access_token"] and _token_cache["expires_at"] > now:
        return _token_cache["access_token"]

    client_id = settings.FATSECRET_CLIENT_ID.strip()
    client_secret = settings.FATSECRET_CLIENT_SECRET.strip()

    if not client_id or not client_secret:
        raise HTTPException(
            status_code=500,
            detail="FATSECRET_CLIENT_ID ou FATSECRET_CLIENT_SECRET não configurado no .env",
        )

    basic_token = base64.b64encode(
        f"{client_id}:{client_secret}".encode("utf-8")
    ).decode("utf-8")

    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.post(
            "https://oauth.fatsecret.com/connect/token",
            headers={
                "Authorization": f"Basic {basic_token}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data={
                "grant_type": "client_credentials",
                "scope": "basic",
            },
        )

    if response.status_code >= 400:
        raise HTTPException(
            status_code=response.status_code,
            detail={
                "message": "Erro ao autenticar na FatSecret",
                "status_code": response.status_code,
                "fatsecret_response": response.text,
            },
        )

    data = response.json()

    _token_cache["access_token"] = data["access_token"]
    _token_cache["expires_at"] = now + int(data.get("expires_in", 3600)) - 60

    return data["access_token"]


async def search_foods(query: str) -> dict[str, Any]:
    token = await get_fatsecret_token()

    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.get(
            "https://platform.fatsecret.com/rest/server.api",
            headers={
                "Authorization": f"Bearer {token}",
            },
            params={
                "method": "foods.search",
                "search_expression": query,
                "format": "json",
                "max_results": 10,
            },
        )

    if response.status_code >= 400:
        raise HTTPException(
            status_code=response.status_code,
            detail={
                "message": "Erro ao buscar alimentos na FatSecret",
                "status_code": response.status_code,
                "fatsecret_response": response.text,
            },
        )

    return response.json()