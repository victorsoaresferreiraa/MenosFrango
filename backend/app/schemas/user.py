"""
Schemas Pydantic para Usuários e Personal Trainer.

Schemas definem o "contrato" da API:
- O que pode entrar (request)
- O que sai (response)
- Validação automática dos dados
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


# ══════════════════════════════════════════════════════════════
# SCHEMAS DE USUÁRIO
# ══════════════════════════════════════════════════════════════

class UserCreate(BaseModel):
    """Dados para criar conta. Role padrão é 'aluno'."""
    email:    EmailStr
    password: str = Field(min_length=8, max_length=128)
    name:     str = Field(min_length=2, max_length=255)
    # NOVO: ao se cadastrar, a pessoa escolhe se é aluno ou personal
    role:     str = Field(default="aluno", pattern="^(aluno|personal)$")


class UserLogin(BaseModel):
    """Dados para login."""
    email:    EmailStr
    password: str


class UserUpdate(BaseModel):
    """Atualização de perfil. Todos os campos são opcionais."""
    name:      Optional[str]   = Field(None, min_length=2, max_length=255)
    height_cm: Optional[float] = Field(None, gt=0, le=300)
    weight_kg: Optional[float] = Field(None, gt=0, le=500)
    age:       Optional[int]   = Field(None, gt=0, le=150)
    goal:      Optional[str]   = Field(None, pattern="^(cutting|bulking|manutencao)$")
    level:     Optional[str]   = Field(None, pattern="^(iniciante|intermediario|avancado)$")
    bio:       Optional[str]   = Field(None, max_length=500)


class UserResponse(BaseModel):
    """Dados do usuário retornados pela API."""
    model_config = {"from_attributes": True}

    id:        UUID
    email:     str
    name:      str
    role:      str          # NOVO
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    age:       Optional[int]   = None
    goal:      Optional[str]   = None
    level:     Optional[str]   = None
    bio:       Optional[str]   = None
    is_active: bool
    is_admin:  bool
    created_at: datetime


class UserPublicResponse(BaseModel):
    """
    Versão resumida do usuário — para o personal ver dados do aluno
    sem expor informações sensíveis como email ou senha.
    """
    model_config = {"from_attributes": True}

    id:        UUID
    name:      str
    goal:      Optional[str] = None
    level:     Optional[str] = None
    weight_kg: Optional[float] = None
    bio:       Optional[str]   = None
    created_at: datetime


# ══════════════════════════════════════════════════════════════
# SCHEMAS DE AUTH
# ══════════════════════════════════════════════════════════════

class TokenResponse(BaseModel):
    """Tokens JWT retornados após login ou registro."""
    access_token:  str
    refresh_token: str
    token_type:    str = "bearer"


class RefreshTokenRequest(BaseModel):
    """Corpo da requisição para renovar o access token."""
    refresh_token: str


# ══════════════════════════════════════════════════════════════
# SCHEMAS DE PERSONAL TRAINER
# ══════════════════════════════════════════════════════════════

class InviteClientRequest(BaseModel):
    """
    O personal convida um aluno pelo email.
    O sistema verifica se o email existe e cria o vínculo.
    """
    client_email: EmailStr
    notes:        Optional[str] = Field(None, max_length=500)


class UpdateClientNotesRequest(BaseModel):
    """Personal atualiza suas anotações sobre o aluno."""
    notes: str = Field(max_length=500)


class PersonalClientResponse(BaseModel):
    """
    Representa um aluno na lista do personal.
    Inclui dados básicos do aluno + status do vínculo.
    """
    model_config = {"from_attributes": True}

    id:          UUID          # ID do vínculo (não do aluno)
    status:      str           # pendente, ativo, inativo
    notes:       Optional[str] = None
    invited_at:  datetime
    accepted_at: Optional[datetime] = None

    # Dados públicos do aluno
    client: UserPublicResponse


class PersonalClientDetailResponse(BaseModel):
    """
    Dados completos de um aluno vistos pelo personal.
    Inclui histórico de treinos, nutrição e KPIs.
    """
    model_config = {"from_attributes": True}

    # Vínculo
    id:     UUID
    status: str
    notes:  Optional[str] = None

    # Dados do aluno
    client: UserPublicResponse

    # KPIs calculados (preenchidos pelo router)
    kpis: Optional[dict] = None


class PersonalDashboardResponse(BaseModel):
    """
    Dashboard do personal trainer.
    Resumo de todos os seus alunos.
    """
    total_clients:   int
    active_clients:  int
    pending_clients: int
    clients:         List[PersonalClientResponse]


class AcceptInviteResponse(BaseModel):
    """Resposta quando aluno aceita um convite."""
    message: str
    personal_name: str
