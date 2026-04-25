"""
Modelos SQLAlchemy para nutrição, fotos e recomendações de IA.
"""
import uuid
from datetime import date, datetime, timezone
from enum import Enum as PyEnum

from sqlalchemy import Date, DateTime, Enum, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class NutritionLog(Base):
    """Registro diário de alimentação do usuário."""

    __tablename__ = "nutrition_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    food_name: Mapped[str] = mapped_column(String(200), nullable=False)
    calories: Mapped[float] = mapped_column(Float, nullable=False)
    protein_g: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    carbs_g: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    fat_g: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    quantity_g: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)

    # Data do registro (sem horário)
    log_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    user: Mapped["User"] = relationship("User", back_populates="nutrition_logs")  # noqa: F821

    def __repr__(self) -> str:
        return f"<NutritionLog {self.food_name} {self.calories}kcal>"


class Photo(Base):
    """Foto corporal enviada pelo usuário."""

    __tablename__ = "photos"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Chave no storage S3/MinIO
    storage_key: Mapped[str] = mapped_column(String(500), nullable=False)

    # Metadados
    weight_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    photo_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    user: Mapped["User"] = relationship("User", back_populates="photos")  # noqa: F821

    def __repr__(self) -> str:
        return f"<Photo {self.photo_date}>"


class AIRecommendationType(str, PyEnum):
    """Tipos de recomendação gerada por IA."""
    WORKOUT_PLAN = "workout_plan"
    NUTRITION_PLAN = "nutrition_plan"
    PROGRESS_ANALYSIS = "progress_analysis"


class AIRecommendation(Base):
    """Recomendação gerada pela camada de IA."""

    __tablename__ = "ai_recommendations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    type: Mapped[AIRecommendationType] = mapped_column(
        Enum(AIRecommendationType), nullable=False, index=True
    )

    # Conteúdo JSON da recomendação
    content: Mapped[dict] = mapped_column(JSONB, nullable=False)

    # Modo IA usado para gerar (A, B ou C)
    ia_mode: Mapped[str] = mapped_column(String(1), default="A", nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    user: Mapped["User"] = relationship("User", back_populates="ai_recommendations")  # noqa: F821

    def __repr__(self) -> str:
        return f"<AIRecommendation {self.type} {self.created_at}>"
