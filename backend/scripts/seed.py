"""
Script de seed — popula banco com dados de demonstração.

Usuários criados:
  demo@menosfrango.ai   / 12345678  → aluno
  personal@menosfrango.ai / 12345678 → personal trainer
  admin@menosfrango.ai  / admin12345 → admin
"""

import asyncio
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import get_db_context
from app.core.security import hash_password
from app.models.nutrition import NutritionLog
from app.models.workout import Workout
from app.models import User, PersonalClient, Workout, NutritionLog, Photo

async def seed():
    print("🌱 Iniciando seed do banco de dados...")

    async with get_db_context() as db:
        from sqlalchemy import select

        # Verifica se já existe
        result = await db.execute(select(User).where(User.email == "demo@menosfrango.ai"))
        if result.scalar_one_or_none():
            print("✅ Seed já executado anteriormente, pulando...")
            return

        # Usuário demo (aluno)
        demo_user = User(
            email="demo@menosfrango.ai",
            hashed_password=hash_password("12345678"),
            name="Demo Aluno Frango",
            role="aluno",
            height_cm=175.0, weight_kg=80.0, age=28,
            goal="bulking", level="intermediario",
            bio="Treino há 2 anos, foco em ganho de massa.",
            is_active=True, is_admin=False,
        )
        db.add(demo_user)

        # Personal demo
        personal_user = User(
            email="personal@menosfrango.ai",
            hashed_password=hash_password("12345678"),
            name="Personal Demo",
            role="personal",
            bio="Especialista em hipertrofia e emagrecimento. CREF 123456-G/SP.",
            is_active=True, is_admin=False,
        )
        db.add(personal_user)

        # Admin
        admin_user = User(
            email="admin@menosfrango.ai",
            hashed_password=hash_password("admin12345"),
            name="Admin",
            role="admin",
            is_active=True, is_admin=True,
        )
        db.add(admin_user)
        await db.flush()

        # Vínculo personal ↔ aluno (já ativo)
        link = PersonalClient(
            personal_id=personal_user.id,
            client_id=demo_user.id,
            status="ativo",
            notes="Aluno focado em bulking. Sem lesões.",
            accepted_at=datetime.now(timezone.utc),
        )
        db.add(link)

        # Treinos dos últimos 30 dias
        exercises = [
            ("Supino Reto", "peito", 4, 10, 80.0),
            ("Agachamento", "quadriceps", 4, 8, 100.0),
            ("Remada Curvada", "costas", 4, 10, 70.0),
            ("Desenvolvimento", "ombros", 3, 12, 40.0),
            ("Rosca Direta", "biceps", 3, 12, 30.0),
            ("Tríceps Testa", "triceps", 3, 12, 25.0),
            ("Levantamento Terra", "posterior", 3, 6, 120.0),
            ("Barra Fixa", "costas", 4, 8, 0.0),
            ("Leg Press", "quadriceps", 3, 15, 150.0),
            ("Hip Thrust", "gluteos", 3, 12, 80.0),
        ]

        now = datetime.now(timezone.utc)
        workout_count = 0
        for day_offset in range(0, 30, 2):
            workout_date = now - timedelta(days=day_offset)
            for i, (exercise, group, sets, reps, weight) in enumerate(exercises[:5]):
                progression = 1 + (day_offset / 30) * 0.05
                workout = Workout(
                    user_id=demo_user.id,
                    exercise=exercise,
                    muscle_group=group,
                    sets=sets, reps=reps,
                    weight_kg=round(weight * progression, 1),
                    rpe=7 + (i % 3),
                    notes=f"Dia {day_offset + 1}",
                    workout_date=workout_date,
                )
                db.add(workout)
                workout_count += 1

        # Registros nutricionais
        foods = [
            ("Frango grelhado", 100, 165, 31, 0, 3.6),
            ("Arroz branco", 100, 130, 2.7, 28, 0.3),
            ("Ovo inteiro", 50, 78, 6, 0.6, 5.3),
            ("Batata doce", 100, 86, 1.6, 20, 0.1),
            ("Whey Protein", 30, 120, 24, 3, 2),
            ("Banana", 100, 89, 1.1, 23, 0.3),
            ("Aveia", 40, 148, 5.2, 25, 2.6),
        ]
        for day_offset in range(14):
            log_date = (now - timedelta(days=day_offset)).date()
            for food_name, qty, cal, prot, carb, fat in foods:
                log = NutritionLog(
                    user_id=demo_user.id,
                    food_name=food_name,
                    quantity_g=qty, calories=cal,
                    protein_g=prot, carbs_g=carb, fat_g=fat,
                    log_date=log_date,
                )
                db.add(log)

        await db.flush()

    print("✅ Seed concluído!")
    print("   🏃 Aluno: demo@menosfrango.ai / 12345678")
    print("   👨‍🏫 Personal: personal@menosfrango.ai / 12345678")
    print("   👑 Admin: admin@menosfrango.ai / admin12345")
    print(f"   🏋️  {workout_count} treinos criados")
    print("   🔗 Vínculo personal↔aluno criado (ativo)")

if __name__ == "__main__":
    asyncio.run(seed())
