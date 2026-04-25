"""
Configurações centrais da aplicação via Pydantic Settings.
Todas as variáveis são lidas do .env automaticamente.
"""

from functools import lru_cache
from typing import List, Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    APP_ENV: Literal["local", "staging", "production"] = "local"
    APP_NAME: str = "Athletic AI"
    API_PORT: int = 8000
    DEBUG: bool = False

    # JWT
    JWT_SECRET: str = "troque_esta_chave"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_EXPIRES_MIN: int = 15
    JWT_REFRESH_EXPIRES_DAYS: int = 7

    # Banco de Dados
    DATABASE_URL: str = "postgresql+psycopg://postgres:postgres@db:5432/athletic_ai"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_ECHO: bool = False

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"

    # Storage S3
    S3_ENDPOINT: str = "http://minio:9000"
    S3_BUCKET: str = "athletic-bucket"
    S3_REGION: str = "sa-east-1"
    S3_ACCESS_KEY: str = "minioadmin"
    S3_SECRET_KEY: str = "minioadmin"
    S3_USE_SSL: bool = False

    # IA
    FEATURE_FLAG_IA_MODE: Literal["A", "B", "C"] = "A"
    OLLAMA_ENDPOINT: str = "http://ollama:11434"
    OLLAMA_MODEL: str = "llama3"
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""

    # Email
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASS: str = ""
    SMTP_FROM: str = "noreply@athletic.ai"
    EMAIL_DEV_LOG: bool = True

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

    # Rate Limit
    RATE_LIMIT_PER_MINUTE: int = 60

    # Celery
    CELERY_BROKER_URL: str = "redis://redis:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/2"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors(cls, v: str) -> str:
        return v

    def get_cors_origins(self) -> List[str]:
        """Retorna lista de origins CORS."""
        return [o.strip() for o in self.CORS_ORIGINS.split(",")]

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"


@lru_cache()
def get_settings() -> Settings:
    """Retorna instância cacheada das configurações."""
    return Settings()


settings = get_settings()
