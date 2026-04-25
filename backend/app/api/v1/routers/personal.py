"""
Router do Personal Trainer.

Todas as rotas aqui exigem que o usuário tenha role='personal'.

Rotas disponíveis:
  GET    /personal/dashboard              → resumo de todos os alunos
  GET    /personal/clients               → lista de alunos
  POST   /personal/clients/invite        → convida aluno pelo email
  GET    /personal/clients/{id}          → detalhes de um aluno
  PUT    /personal/clients/{id}/notes    → atualiza notas do aluno
  DELETE /personal/clients/{id}          → desativa vínculo
  GET    /personal/clients/{id}/workouts → treinos do aluno
  GET    /personal/clients/{id}/nutrition → nutrição do aluno
  POST   /personal/clients/{id}/ai/workout-plan   → gera plano via IA para o aluno
  POST   /personal/clients/{id}/ai/nutrition-plan → gera plano nutricional para o aluno
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User, UserRole
from app.models.workout import Workout
from app.models.nutrition import NutritionLog
from app.repositories.personal import PersonalClientRepository
from app.repositories.user import UserRepository
from app.repositories.workout import WorkoutRepository
from app.schemas.personal import (
    AcceptInviteResponse,
    InviteClientRequest,
    PersonalClientDetailResponse,
    PersonalClientResponse,
    PersonalDashboardResponse,
    UpdateClientNotesRequest,
)
from app.schemas.ai import WorkoutPlanRequest, NutritionPlanRequest
from app.services.ai.base import get_ai_service

router = APIRouter(prefix="/personal", tags=["personal"])


# ── Dependência: garante que só personais acessem ───────────

async def require_personal(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependência que verifica se o usuário é personal.
    Se não for, retorna 403 Forbidden.
    """
    if current_user.role != UserRole.personal:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a personal trainers.",
        )
    return current_user


# ══════════════════════════════════════════════════════════════
# DASHBOARD DO PERSONAL
# ══════════════════════════════════════════════════════════════

@router.get("/dashboard", response_model=PersonalDashboardResponse)
async def get_personal_dashboard(
    personal: User = Depends(require_personal),
    db: AsyncSession = Depends(get_db),
):
    """
    Dashboard do personal trainer.
    Mostra contagem de alunos e lista geral.
    """
    repo = PersonalClientRepository(db)

    counts  = await repo.count_clients(personal.id)
    clients = await repo.get_clients_of_personal(personal.id)

    return PersonalDashboardResponse(
        total_clients=counts["total"],
        active_clients=counts["ativo"],
        pending_clients=counts["pendente"],
        clients=[PersonalClientResponse.model_validate(c) for c in clients],
    )


# ══════════════════════════════════════════════════════════════
# GERENCIAR ALUNOS
# ══════════════════════════════════════════════════════════════

@router.get("/clients", response_model=list[PersonalClientResponse])
async def list_clients(
    personal: User = Depends(require_personal),
    db: AsyncSession = Depends(get_db),
):
    """Lista todos os alunos do personal (todos os status)."""
    repo    = PersonalClientRepository(db)
    clients = await repo.get_clients_of_personal(personal.id)
    return [PersonalClientResponse.model_validate(c) for c in clients]


@router.post("/clients/invite", response_model=PersonalClientResponse, status_code=201)
async def invite_client(
    data: InviteClientRequest,
    personal: User = Depends(require_personal),
    db: AsyncSession = Depends(get_db),
):
    """
    Personal convida um aluno pelo e-mail.

    Fluxo:
    1. Verifica se o e-mail existe no sistema
    2. Verifica se o usuário encontrado é do tipo 'aluno'
    3. Verifica se já existe um vínculo entre os dois
    4. Cria o vínculo com status 'pendente'
    """
    user_repo = UserRepository(db)
    pc_repo   = PersonalClientRepository(db)

    # 1. Busca o aluno pelo email
    client = await user_repo.get_by_email(data.client_email)
    if not client:
        raise HTTPException(
            status_code=404,
            detail="Nenhum usuário encontrado com esse e-mail.",
        )

    # 2. Verifica se é aluno (não pode convidar outro personal)
    if client.role != UserRole.aluno:
        raise HTTPException(
            status_code=400,
            detail="Este usuário não é um aluno.",
        )

    # 3. Não pode se convidar
    if client.id == personal.id:
        raise HTTPException(status_code=400, detail="Você não pode se convidar.")

    # 4. Verifica se já existe vínculo
    existing = await pc_repo.get_link(personal.id, client.id)
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"Já existe um vínculo com este aluno (status: {existing.status}).",
        )

    # 5. Cria o convite
    link = await pc_repo.create_invite(
        personal_id=personal.id,
        client_id=client.id,
        notes=data.notes,
    )

    # Recarrega com dados do aluno
    from sqlalchemy.orm import selectinload
    from sqlalchemy import select as sa_select
    from app.models.user import PersonalClient
    result = await db.execute(
        sa_select(PersonalClient)
        .where(PersonalClient.id == link.id)
        .options(selectinload(PersonalClient.client))
    )
    link = result.scalar_one()

    return PersonalClientResponse.model_validate(link)


@router.get("/clients/{client_id}", response_model=PersonalClientDetailResponse)
async def get_client_detail(
    client_id: UUID,
    personal: User = Depends(require_personal),
    db: AsyncSession = Depends(get_db),
):
    """
    Detalhes de um aluno específico.
    Inclui dados pessoais, KPIs de treino e nutrição.
    """
    pc_repo = PersonalClientRepository(db)

    # Verifica se este aluno pertence ao personal
    link = await pc_repo.get_link(personal.id, client_id)
    if not link:
        raise HTTPException(status_code=404, detail="Aluno não encontrado.")

    # Busca KPIs do aluno
    from datetime import datetime, timedelta, timezone
    from sqlalchemy import func
    now = datetime.now(timezone.utc)
    thirty_days_ago = now - timedelta(days=30)

    # Total de treinos nos últimos 30 dias
    result = await db.execute(
        select(func.count(Workout.id)).where(
            Workout.user_id == client_id,
            Workout.workout_date >= thirty_days_ago,
        )
    )
    total_workouts = result.scalar_one() or 0

    # Volume total
    result = await db.execute(
        select(func.sum(Workout.weight_kg * Workout.sets * Workout.reps)).where(
            Workout.user_id == client_id,
            Workout.workout_date >= thirty_days_ago,
        )
    )
    total_volume = result.scalar_one() or 0

    kpis = {
        "workouts_last_30d": total_workouts,
        "total_volume_kg": round(float(total_volume), 1),
    }

    response = PersonalClientDetailResponse.model_validate(link)
    response.kpis = kpis
    return response


@router.put("/clients/{client_id}/notes", response_model=PersonalClientResponse)
async def update_client_notes(
    client_id: UUID,
    data: UpdateClientNotesRequest,
    personal: User = Depends(require_personal),
    db: AsyncSession = Depends(get_db),
):
    """Personal atualiza suas anotações sobre o aluno."""
    pc_repo = PersonalClientRepository(db)
    link = await pc_repo.get_link(personal.id, client_id)
    if not link:
        raise HTTPException(status_code=404, detail="Aluno não encontrado.")

    link = await pc_repo.update_notes(link, data.notes)
    return PersonalClientResponse.model_validate(link)


@router.delete("/clients/{client_id}", status_code=204)
async def remove_client(
    client_id: UUID,
    personal: User = Depends(require_personal),
    db: AsyncSession = Depends(get_db),
):
    """Desativa o vínculo com o aluno (não deleta os dados do aluno)."""
    pc_repo = PersonalClientRepository(db)
    link = await pc_repo.get_link(personal.id, client_id)
    if not link:
        raise HTTPException(status_code=404, detail="Aluno não encontrado.")

    await pc_repo.deactivate(link)


# ══════════════════════════════════════════════════════════════
# VER DADOS DO ALUNO
# ══════════════════════════════════════════════════════════════

@router.get("/clients/{client_id}/workouts")
async def get_client_workouts(
    client_id: UUID,
    personal: User = Depends(require_personal),
    db: AsyncSession = Depends(get_db),
    page: int = 1,
    page_size: int = 20,
):
    """
    Personal vê o histórico de treinos do aluno.
    Só funciona se o aluno estiver ativo.
    """
    pc_repo = PersonalClientRepository(db)
    link = await pc_repo.get_link(personal.id, client_id)

    if not link or link.status != "ativo":
        raise HTTPException(
            status_code=403,
            detail="Acesso negado. O aluno precisa estar ativo.",
        )

    workout_repo = WorkoutRepository(db)
    items, total = await workout_repo.get_list(
        user_id=client_id, page=page, page_size=page_size
    )
    return {
        "items": [
            {
                "id": str(w.id),
                "exercise": w.exercise,
                "muscle_group": w.muscle_group,
                "sets": w.sets,
                "reps": w.reps,
                "weight_kg": w.weight_kg,
                "rpe": w.rpe,
                "workout_date": w.workout_date.isoformat(),
            }
            for w in items
        ],
        "total": total,
        "page": page,
    }


@router.get("/clients/{client_id}/nutrition")
async def get_client_nutrition(
    client_id: UUID,
    personal: User = Depends(require_personal),
    db: AsyncSession = Depends(get_db),
):
    """Personal vê o resumo nutricional dos últimos 7 dias do aluno."""
    pc_repo = PersonalClientRepository(db)
    link = await pc_repo.get_link(personal.id, client_id)

    if not link or link.status != "ativo":
        raise HTTPException(status_code=403, detail="Acesso negado.")

    from datetime import datetime, timedelta, timezone
    from sqlalchemy import func
    now = datetime.now(timezone.utc)
    seven_days_ago = (now - timedelta(days=7)).date()

    result = await db.execute(
        select(
            func.sum(NutritionLog.calories).label("calories"),
            func.sum(NutritionLog.protein_g).label("protein"),
            func.avg(NutritionLog.calories).label("avg_calories"),
        ).where(
            NutritionLog.user_id == client_id,
            NutritionLog.log_date >= seven_days_ago,
        )
    )
    row = result.one()
    return {
        "period": "últimos 7 dias",
        "total_calories": round(float(row.calories or 0), 1),
        "total_protein_g": round(float(row.protein or 0), 1),
        "avg_daily_calories": round(float(row.avg_calories or 0), 1),
    }


# ══════════════════════════════════════════════════════════════
# IA PARA O ALUNO
# ══════════════════════════════════════════════════════════════

@router.post("/clients/{client_id}/ai/workout-plan")
async def generate_workout_plan_for_client(
    client_id: UUID,
    data: WorkoutPlanRequest,
    personal: User = Depends(require_personal),
    db: AsyncSession = Depends(get_db),
):
    """
    Personal gera um plano de treino via IA para o aluno.
    O plano é salvo no histórico de recomendações do ALUNO.
    """
    pc_repo = PersonalClientRepository(db)
    link = await pc_repo.get_link(personal.id, client_id)

    if not link or link.status != "ativo":
        raise HTTPException(status_code=403, detail="Acesso negado.")

    ai = get_ai_service()
    payload = await ai.generate_workout_plan(data.model_dump())

    # Salva como recomendação do aluno (não do personal)
    from app.models.ai_recommendation import AIRecommendation
    rec = AIRecommendation(
        user_id=client_id,
        type="workout_plan",
        payload={
            **payload,
            "generated_by_personal": str(personal.id),
            "personal_name": personal.name,
        },
        ia_mode=payload.get("ia_mode", "A"),
    )
    db.add(rec)
    await db.flush()
    await db.refresh(rec)

    return {
        "message": f"Plano gerado para o aluno por {personal.name}",
        "plan": payload,
    }


@router.post("/clients/{client_id}/ai/nutrition-plan")
async def generate_nutrition_plan_for_client(
    client_id: UUID,
    data: NutritionPlanRequest,
    personal: User = Depends(require_personal),
    db: AsyncSession = Depends(get_db),
):
    """Personal gera plano nutricional via IA para o aluno."""
    pc_repo = PersonalClientRepository(db)
    link = await pc_repo.get_link(personal.id, client_id)

    if not link or link.status != "ativo":
        raise HTTPException(status_code=403, detail="Acesso negado.")

    ai = get_ai_service()
    payload = await ai.generate_nutrition_plan(data.model_dump())

    from app.models.ai_recommendation import AIRecommendation
    rec = AIRecommendation(
        user_id=client_id,
        type="nutrition_plan",
        payload={
            **payload,
            "generated_by_personal": str(personal.id),
            "personal_name": personal.name,
        },
        ia_mode=payload.get("ia_mode", "A"),
    )
    db.add(rec)
    await db.flush()
    await db.refresh(rec)

    return {
        "message": f"Plano nutricional gerado para o aluno por {personal.name}",
        "plan": payload,
    }


# ══════════════════════════════════════════════════════════════
# ROTAS DO ALUNO (aceitar convite, ver personais)
# ══════════════════════════════════════════════════════════════

@router.get("/my-personals")
async def get_my_personals(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Aluno vê a lista de personais que o convidaram.
    Disponível para qualquer usuário logado.
    """
    pc_repo = PersonalClientRepository(db)
    links = await pc_repo.get_personals_of_client(current_user.id)
    return [
        {
            "id": str(link.id),
            "personal_name": link.personal.name,
            "status": link.status,
            "invited_at": link.invited_at.isoformat(),
        }
        for link in links
    ]


@router.post("/accept-invite/{link_id}", response_model=AcceptInviteResponse)
async def accept_invite(
    link_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Aluno aceita o convite de um personal.
    Só o próprio aluno pode aceitar.
    """
    pc_repo = PersonalClientRepository(db)
    link = await pc_repo.get_link_by_id(link_id)

    if not link:
        raise HTTPException(status_code=404, detail="Convite não encontrado.")

    # Verifica se este convite é para este aluno
    if link.client_id != current_user.id:
        raise HTTPException(status_code=403, detail="Este convite não é para você.")

    if link.status != "pendente":
        raise HTTPException(
            status_code=400,
            detail=f"Este convite já foi processado (status: {link.status}).",
        )

    await pc_repo.accept_invite(link)

    return AcceptInviteResponse(
        message="Convite aceito! Seu personal agora pode acompanhar seus treinos.",
        personal_name=link.personal.name,
    )
