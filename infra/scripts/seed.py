"""
Script de seed para popular o banco com dados de demonstração.
Cria usuário demo e dados de exemplo para todas as funcionalidades.

Uso:
    python infra/scripts/seed.py
    # ou via Docker:
    docker compose exec api python infra/scripts/seed.py
"""
import asyncio
import os
import sys
import uuid
from datetime import date, datetime, timedelta, timezone
from random import choice, randint, uniform

# Adiciona o backend ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.core.security import hash_password
from app.models.nutrition_photo_ai import AIRecommendation, AIRecommendationType, NutritionLog
from app.models.user import NivelEnum, ObjetivoEnum, User
from app.models.workout import Workout

settings = get_settings()

EXERCISES = {
    "Peitoral": ["Supino Reto", "Supino Inclinado", "Crucifixo"],
    "Costas": ["Puxada Frontal", "Remada Curvada", "Levantamento Terra"],
    "Ombros": ["Desenvolvimento Militar", "Elevação Lateral"],
    "Bíceps": ["Rosca Direta", "Rosca Alternada"],
    "Tríceps": ["Tríceps Pulley", "Tríceps Testa"],
    "Quadríceps": ["Agachamento", "Leg Press", "Extensora"],
    "Posterior": ["Stiff", "Mesa Flexora"],
    "Glúteos": ["Hip Thrust", "Agachamento Sumô"],
    "Abdômen": ["Abdominal Crunch", "Prancha"],
}

FOODS = [
    ("Frango Grelhado", 165, 31, 0, 3.6),
    ("Arroz Integral", 216, 5, 45, 1.8),
    ("Ovo Cozido", 155, 13, 1.1, 11),
    ("Batata-Doce", 86, 1.6, 20, 0.1),
    ("Whey Protein", 120, 24, 3, 1.5),
    ("Aveia", 389, 17, 66, 7),
    ("Banana", 89, 1.1, 23, 0.3),
    ("Peito de Peru", 135, 28, 0, 2),
    ("Azeite", 884, 0, 0, 100),
    ("Feijão Cozido", 127, 8.7, 22, 0.5),
]


async def seed(db: AsyncSession) -> None:
    """Insere dados de demonstração."""
    print("🌱 Iniciando seed de dados...")

    # ── Usuário demo ──────────────────────────────────────
    demo_user = User(
        id=uuid.uuid4(),
        email="demo@athletic.ai",
        hashed_password=hash_password("12345678"),
        name="Demo Atleta",
        height_cm=175.0,
        weight_kg=80.0,
        age=28,
        objetivo=ObjetivoEnum.BULKING,
        nivel=NivelEnum.INTERMEDIARIO,
        is_active=True,
        is_verified=True,
    )
    db.add(demo_user)

    # ── Usuário admin ─────────────────────────────────────
    admin_user = User(
        id=uuid.uuid4(),
        email="admin@athletic.ai",
        hashed_password=hash_password("admin1234"),
        name="Admin",
        height_cm=180.0,
        weight_kg=85.0,
        age=35,
        objetivo=ObjetivoEnum.MANUTENCAO,
        nivel=NivelEnum.AVANCADO,
        is_active=True,
        is_verified=True,
        is_admin=True,
    )
    db.add(admin_user)
    await db.flush()

    print(f"✅ Usuários criados: {demo_user.email}, {admin_user.email}")

    # ── Treinos (últimos 60 dias) ─────────────────────────
    workout_count = 0
    for days_ago in range(60, 0, -1):
        # ~4 dias de treino por semana
        if days_ago % 7 in (1, 2, 4, 6):
            performed_at = datetime.now(timezone.utc) - timedelta(days=days_ago)
            muscle_group = choice(list(EXERCISES.keys()))
            exercise = choice(EXERCISES[muscle_group])
            base_weight = randint(20, 100)

            workout = Workout(
                user_id=demo_user.id,
                exercise=exercise,
                muscle_group=muscle_group,
                sets=randint(3, 5),
                reps=randint(6, 12),
                weight_kg=round(base_weight + uniform(-5, 5), 1),
                rpe=randint(6, 9),
                notes="",
                performed_at=performed_at,
            )
            db.add(workout)
            workout_count += 1

    print(f"✅ {workout_count} treinos criados")

    # ── Registros nutricionais (últimos 30 dias) ──────────
    nutrition_count = 0
    for days_ago in range(30, 0, -1):
        log_date = date.today() - timedelta(days=days_ago)
        for _ in range(randint(3, 5)):  # 3-5 refeições por dia
            food = choice(FOODS)
            qty = uniform(80, 300)
            factor = qty / 100

            log = NutritionLog(
                user_id=demo_user.id,
                food_name=food[0],
                calories=round(food[1] * factor, 1),
                protein_g=round(food[2] * factor, 1),
                carbs_g=round(food[3] * factor, 1),
                fat_g=round(food[4] * factor, 1),
                quantity_g=round(qty, 1),
                log_date=log_date,
            )
            db.add(log)
            nutrition_count += 1

    print(f"✅ {nutrition_count} registros nutricionais criados")

    # ── Recomendação de IA ─────────────────────────────────
    rec = AIRecommendation(
        user_id=demo_user.id,
        type=AIRecommendationType.WORKOUT_PLAN,
        content={
            "split_type": "upper_lower",
            "weekly_frequency": 4,
            "ia_mode": "A",
            "message": "Plano gerado automaticamente para demonstração",
        },
        ia_mode="A",
    )
    db.add(rec)

    await db.commit()

    print("\n" + "=" * 50)
    print("🎉 Seed concluído com sucesso!")
    print("=" * 50)
    print("📧 Login demo:  demo@athletic.ai / 12345678")
    print("👑 Login admin: admin@athletic.ai / admin1234")
    print("🌐 Frontend:    http://localhost:3000")
    print("📚 API Docs:    http://localhost:8000/docs")
    print("=" * 50)


async def main() -> None:
    engine = create_async_engine(settings.database_url, echo=False)
    session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as session:
        # Verifica se usuário demo já existe
        from sqlalchemy import select
        result = await session.execute(select(User).where(User.email == "demo@athletic.ai"))
        if result.scalar_one_or_none():
            print("⚠️  Dados demo já existem. Use 'make clean' para resetar.")
            return
        await seed(session)

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
