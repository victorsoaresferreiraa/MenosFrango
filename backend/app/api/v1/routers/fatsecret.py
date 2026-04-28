from fastapi import APIRouter, Query

from app.services.fatsecret_service import search_foods

router = APIRouter(prefix="/fatsecret", tags=["FatSecret"])


@router.get("/foods/search")
async def fatsecret_search_foods(
    q: str = Query(..., min_length=2),
):
    return await search_foods(q)