"""Agrega todos os routers da v1."""

from fastapi import APIRouter

from app.api.v1.routers.auth import router as auth_router
from app.api.v1.routers.users import router as users_router
from app.api.v1.routers.workouts import router as workouts_router
from app.api.v1.routers.nutrition import router as nutrition_router
from app.api.v1.routers.photos import router as photos_router
from app.api.v1.routers.dashboard import router as dashboard_router
from app.api.v1.routers.ai import router as ai_router
from app.api.v1.routers.admin import router as admin_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(workouts_router)
api_router.include_router(nutrition_router)
api_router.include_router(photos_router)
api_router.include_router(dashboard_router)
api_router.include_router(ai_router)
api_router.include_router(admin_router)
