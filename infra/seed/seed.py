#!/usr/bin/env python3
"""Script de seed — cria dados demo para desenvolvimento."""

import asyncio
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.core.config import get_settings
from app.core.security import hash_password
from app.models import User, Workout, NutritionLog, AIRecommendation

settings = get_settings()


async def seed():
    print("🌱 Iniciando seed...")
    engine = create_async_engine(settings.database_url, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as db:
        # Usuário demo
        demo = User(
            email="demo@athletic.ai",
            hashed_password=hash_password("12345678"),
            nome="Demo User", altura=175.0, peso=80.0, idade=28,
            objetivo="bulking", nivel="intermediario", is_active=True,
        )
        db.add(demo)
        await db.flush()

        admin = User(
            email="admin@athletic.ai",
            hashed_password=hash_password("admin1234"),
            nome="Admin", is_admin=True, is_active=True,
        )
        db.add(admin)
        await db.flush()

        # Treinos
        exercicios = [
            ("Supino Reto", "peito", 4, 10, 80.0),
            ("Puxada Frontal", "costas", 4, 12, 60.0),
            ("Agachamento", "quadriceps", 4, 8, 100.0),
            ("Desenvolvimento", "ombro", 3, 12, 40.0),
            ("Rosca Direta", "biceps", 3, 12, 30.0),
            ("Tríceps Pulley", "triceps", 3, 15, 35.0),
        ]
        for i in range(20):
            e = exercicios[i % len(exercicios)]
            db.add(Workout(
                user_id=demo.id, exercicio=e[0], grupo_muscular=e[1],
                series=e[2], reps=e[3], carga_kg=e[4] + (i // 6) * 2.5,
                data_hora=datetime.now(timezone.utc) - timedelta(days=20 - i),
            ))

        # Nutrição
        for day in range(14):
            d = (datetime.now(timezone.utc) - timedelta(days=day)).date()
            for alimento, cal, prot, carb, gord in [
                ("Frango 200g", 330, 62, 0, 7),
                ("Arroz 100g", 123, 2.6, 25.8, 1),
                ("Whey protein", 120, 25, 3, 1.5),
            ]:
                db.add(NutritionLog(
                    user_id=demo.id, alimento=alimento, calorias=cal,
                    proteinas=prot, carboidratos=carb, gorduras=gord, data=d,
                ))

        await db.commit()
        print("✅ Seed concluído!")
        print("   demo@athletic.ai / 12345678")
        print("   admin@athletic.ai / admin1234")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
