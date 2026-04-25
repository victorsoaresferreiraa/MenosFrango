"""
MENOSFRANGO — FastAPI Application Entry Point

NOVIDADE: inclui o router do personal trainer
"""

import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

# Routers existentes
from app.api.v1.routers import (
    auth, users, workouts, nutrition,
    photos, dashboard, ai, reports,
)
# NOVO: router do personal
from app.api.v1.routers.personal import router as personal_router

from app.core.config import settings
from app.core.logging import get_logger, setup_logging

setup_logging(debug=settings.DEBUG)
logger = get_logger(__name__)

limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("athletic_ai_startup", env=settings.APP_ENV)
    try:
        from app.core.database import engine
        async with engine.connect() as conn:
            await conn.execute(__import__("sqlalchemy").text("SELECT 1"))
        logger.info("database_connected")
    except Exception as e:
        logger.error("database_connection_failed", error=str(e))
    yield
    logger.info("athletic_ai_shutdown")


app = FastAPI(
    title="MENOSFRANGO",
    description="Plataforma de treinos e nutrição com IA para personais e alunos",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())[:8]
    start_time = time.time()
    request.state.request_id = request_id
    response: Response = await call_next(request)
    duration_ms = round((time.time() - start_time) * 1000, 1)
    logger.info(
        "http_request",
        method=request.method,
        path=request.url.path,
        status=response.status_code,
        duration_ms=duration_ms,
        request_id=request_id,
    )
    response.headers["X-Request-ID"] = request_id
    return response


# ── Registra todos os routers ────────────────────────────────
PREFIX = "/api/v1"
app.include_router(auth.router,      prefix=PREFIX)
app.include_router(users.router,     prefix=PREFIX)
app.include_router(workouts.router,  prefix=PREFIX)
app.include_router(nutrition.router, prefix=PREFIX)
app.include_router(photos.router,    prefix=PREFIX)
app.include_router(dashboard.router, prefix=PREFIX)
app.include_router(ai.router,        prefix=PREFIX)
app.include_router(reports.router,   prefix=PREFIX)
app.include_router(personal_router,  prefix=PREFIX)  # NOVO


@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "1.0.0"}


@app.get("/")
async def root():
    return {"message": "MENOSFRANGO — Plataforma para Personais e Alunos"}
