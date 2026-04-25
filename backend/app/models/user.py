"""
Modelos SQLAlchemy para Usuários.

NOVIDADES nesta versão:
- Campo 'role' no User (aluno, personal, admin)
- Novo modelo PersonalClient (relaciona personal ↔ aluno)
"""

import uuid
from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


# ── Enums (categorias fixas) ────────────────────────────────

class UserRole(str, Enum):
    """
    Tipo de usuário no sistema.
    - aluno:    usuário comum, registra treinos e nutrição
    - personal: personal trainer, gerencia alunos
    - admin:    dono da plataforma
    """
    aluno    = "aluno"
    personal = "personal"
    admin    = "admin"


class UserGoal(str, Enum):
    cutting    = "cutting"
    bulking    = "bulking"
    manutencao = "manutencao"


class UserLevel(str, Enum):
    iniciante     = "iniciante"
    intermediario = "intermediario"
    avancado      = "avancado"


class ClientStatus(str, Enum):
    """
    Status do relacionamento personal ↔ aluno.
    - pendente: convite enviado, aluno ainda não aceitou
    - ativo:    aluno aceitou, personal pode acompanhar
    - inativo:  relacionamento encerrado
    """
    pendente = "pendente"
    ativo    = "ativo"
    inativo  = "inativo"


# ── Modelo User ─────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    # ── NOVO: papel do usuário no sistema ───────────────────
    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=UserRole.aluno,
        server_default="aluno",
    )

    # Dados físicos (opcional, usado para cálculos da IA)
    height_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    weight_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    age: Mapped[int | None]         = mapped_column(Integer, nullable=True)

    # Objetivo e nível de treino
    goal:  Mapped[str | None] = mapped_column(String(50), nullable=True)
    level: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Bio pública (visível para o personal/aluno)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Status da conta
    is_active: Mapped[bool] = mapped_column(Boolean, default=True,  nullable=False)
    is_admin:  Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=text("NOW()"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        server_default=text("NOW()"),
    )

    # ── Relacionamentos com outros dados do usuário ─────────
    workouts: Mapped[list["Workout"]] = relationship(
        "Workout", back_populates="user", cascade="all, delete-orphan"
    )
    photos: Mapped[list["Photo"]] = relationship(
        "Photo", back_populates="user", cascade="all, delete-orphan"
    )
    nutrition_logs: Mapped[list["NutritionLog"]] = relationship(
        "NutritionLog", back_populates="user", cascade="all, delete-orphan"
    )
    ai_recommendations: Mapped[list["AIRecommendation"]] = relationship(
        "AIRecommendation", back_populates="user", cascade="all, delete-orphan"
    )

    # ── NOVOS: relacionamentos personal ↔ aluno ─────────────

    # Quando este usuário É o personal (lista de alunos dele)
    my_clients: Mapped[list["PersonalClient"]] = relationship(
        "PersonalClient",
        foreign_keys="PersonalClient.personal_id",
        back_populates="personal",
        cascade="all, delete-orphan",
    )

    # Quando este usuário É o aluno (lista de personais dele)
    my_personals: Mapped[list["PersonalClient"]] = relationship(
        "PersonalClient",
        foreign_keys="PersonalClient.client_id",
        back_populates="client",
        cascade="all, delete-orphan",
    )

    # ── Helpers ─────────────────────────────────────────────

    @property
    def is_personal(self) -> bool:
        return self.role == UserRole.personal

    @property
    def is_aluno(self) -> bool:
        return self.role == UserRole.aluno

    def __repr__(self) -> str:
        return f"<User {self.email} role={self.role}>"


# ── Modelo PersonalClient ────────────────────────────────────

class PersonalClient(Base):
    """
    Tabela de relacionamento entre Personal e Aluno.

    Analogia: é como uma lista de contatos do personal.
    Cada linha = um aluno vinculado a um personal.
    """
    __tablename__ = "personal_clients"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )

    # FK para o personal trainer
    personal_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # FK para o aluno
    client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Status do vínculo
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=ClientStatus.pendente,
        server_default="pendente",
    )

    # Notas privadas do personal sobre o aluno
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Timestamps
    invited_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=text("NOW()"),
    )
    accepted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relacionamentos ORM
    personal: Mapped["User"] = relationship(
        "User", foreign_keys=[personal_id], back_populates="my_clients"
    )
    client: Mapped["User"] = relationship(
        "User", foreign_keys=[client_id], back_populates="my_personals"
    )

    def __repr__(self) -> str:
        return f"<PersonalClient personal={self.personal_id} client={self.client_id} status={self.status}>"
