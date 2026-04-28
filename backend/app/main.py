"""
MENOSFRANGO — FastAPI Application Entry Point
"""

import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.api.v1.routers import (
    auth,
    users,
    workouts,
    nutrition,
    photos,
    dashboard,
    ai,
    reports,
    fatsecret,
)

from app.api.v1.routers.personal import router as personal_router
from app.api.v1.routers.admin import router as admin_router

from app.core.config import settings
from app.core.logging import get_logger, setup_logging


setup_logging(debug=settings.DEBUG)
logger = get_logger(__name__)

limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("menosfrango_startup", env=settings.APP_ENV)

    try:
        from app.core.database import engine
        import sqlalchemy

        async with engine.connect() as conn:
            await conn.execute(sqlalchemy.text("SELECT 1"))

        logger.info("database_connected")

    except Exception as e:
        logger.error("database_connection_failed", error=str(e))

    yield

    logger.info("menosfrango_shutdown")


app = FastAPI(
    title="MENOSFRANGO API",
    description="Plataforma de treinos e nutrição com IA para personais e alunos",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


# ─────────────────────────────────────────────
# CORS
# ─────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)


# ─────────────────────────────────────────────
# Rate limit
# ─────────────────────────────────────────────

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# ─────────────────────────────────────────────
# Middleware de log seguro
# ─────────────────────────────────────────────

@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())[:8]
    start_time = time.time()

    try:
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

    except Exception as e:
        duration_ms = round((time.time() - start_time) * 1000, 1)

        logger.error(
            "http_request_failed",
            method=request.method,
            path=request.url.path,
            error=str(e),
            duration_ms=duration_ms,
            request_id=request_id,
        )

        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "error": str(e),
                "request_id": request_id,
            },
            headers={
                "X-Request-ID": request_id,
            },
        )


# ─────────────────────────────────────────────
# Routers
# ─────────────────────────────────────────────

PREFIX = "/api/v1"

app.include_router(auth.router, prefix=PREFIX)
app.include_router(users.router, prefix=PREFIX)
app.include_router(workouts.router, prefix=PREFIX)
app.include_router(nutrition.router, prefix=PREFIX)
app.include_router(photos.router, prefix=PREFIX)
app.include_router(dashboard.router, prefix=PREFIX)
app.include_router(ai.router, prefix=PREFIX)
app.include_router(reports.router, prefix=PREFIX)
app.include_router(fatsecret.router, prefix=PREFIX)
app.include_router(personal_router, prefix=PREFIX)
app.include_router(admin_router, prefix=PREFIX)



# ─────────────────────────────────────────────
# Health check
# ─────────────────────────────────────────────

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "version": "2.0.0",
    }


@app.get("/")
async def root():
    return {
        "message": "MENOSFRANGO — Plataforma para Personais e Alunos 🐔🤖"
    }