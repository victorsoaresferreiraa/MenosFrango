"""
Testes da camada de IA (Modo A — offline).
"""
import pytest

from app.models.user import NivelEnum, ObjetivoEnum, User
from app.services.ai.ia_service import HeuristicAI


def make_user(**kwargs) -> User:
    """Helper para criar usuário de teste."""
    user = User()
    user.weight_kg = kwargs.get("weight_kg", 80.0)
    user.height_cm = kwargs.get("height_cm", 175.0)
    user.age = kwargs.get("age", 30)
    user.objetivo = kwargs.get("objetivo", ObjetivoEnum.MANUTENCAO)
    user.nivel = kwargs.get("nivel", NivelEnum.INICIANTE)
    return user


class TestHeuristicAI:
    def test_tdee_calculation(self):
        """TDEE calculado deve estar em range razoável."""
        ai = HeuristicAI()
        user = make_user(weight_kg=80, height_cm=175, age=30, nivel=NivelEnum.INTERMEDIARIO)
        tdee = ai.calculate_tdee(user)
        assert 1800 <= tdee <= 4000, f"TDEE fora do range: {tdee}"

    def test_tdee_without_data(self):
        """TDEE com dados ausentes retorna valor padrão."""
        ai = HeuristicAI()
        user = User()
        user.weight_kg = None
        user.height_cm = None
        user.age = None
        user.nivel = NivelEnum.INICIANTE
        tdee = ai.calculate_tdee(user)
        assert tdee == 2000.0

    def test_nutrition_plan_cutting(self):
        """Plano de cutting tem déficit calórico."""
        ai = HeuristicAI()
        user = make_user(objetivo=ObjetivoEnum.CUTTING)
        plan = ai.generate_nutrition_plan(user)

        assert plan["target_calories"] < plan["tdee"]
        assert plan["protein_g"] > 0
        assert plan["carbs_g"] > 0
        assert plan["fat_g"] > 0
        assert plan["ia_mode"] == "A"

    def test_nutrition_plan_bulking(self):
        """Plano de bulking tem superávit calórico."""
        ai = HeuristicAI()
        user = make_user(objetivo=ObjetivoEnum.BULKING)
        plan = ai.generate_nutrition_plan(user)
        assert plan["target_calories"] > plan["tdee"]

    def test_workout_plan_full_body(self):
        """Frequência <= 2 gera Full Body."""
        ai = HeuristicAI()
        user = make_user(nivel=NivelEnum.INICIANTE)
        plan = ai.generate_workout_plan(user, weekly_frequency=2)
        assert plan["split_type"] == "full_body"
        assert len(plan["weeks"]) == 4
        assert plan["ia_mode"] == "A"

    def test_workout_plan_upper_lower(self):
        """Frequência 3-4 gera Upper/Lower."""
        ai = HeuristicAI()
        user = make_user(nivel=NivelEnum.INTERMEDIARIO)
        plan = ai.generate_workout_plan(user, weekly_frequency=4)
        assert plan["split_type"] == "upper_lower"

    def test_workout_plan_ppl(self):
        """Frequência >= 5 gera PPL."""
        ai = HeuristicAI()
        user = make_user(nivel=NivelEnum.AVANCADO)
        plan = ai.generate_workout_plan(user, weekly_frequency=6)
        assert plan["split_type"] == "ppl"

    def test_workout_plan_has_deload(self):
        """Plano sempre inclui semana de deload."""
        ai = HeuristicAI()
        user = make_user()
        plan = ai.generate_workout_plan(user)
        deload_weeks = [w for w in plan["weeks"] if w["type"] == "deload"]
        assert len(deload_weeks) >= 1

    def test_analyze_progress_no_data(self):
        """Análise sem dados retorna mensagem adequada."""
        ai = HeuristicAI()
        user = make_user()
        result = ai.analyze_progress([], [])
        assert "Sem dados" in result["summary"]

    def test_analyze_progress_with_data(self):
        """Análise com dados retorna recomendações."""
        ai = HeuristicAI()
        user = make_user()
        workouts = [{"sets": 4, "reps": 10, "weight_kg": 80} for _ in range(10)]
        result = ai.analyze_progress(workouts, [{"weight_kg": 80}])
        assert "recommendations" in result
        assert len(result["recommendations"]) > 0


@pytest.mark.asyncio
class TestAIEndpoints:
    async def test_generate_workout_plan(self, client, auth_headers):
        """POST /ai/workout-plan retorna plano gerado."""
        resp = await client.post(
            "/api/v1/ai/workout-plan",
            json={"weekly_frequency": 4, "limitations": ""},
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert "plan" in data
        assert data["plan"]["ia_mode"] == "A"

    async def test_generate_nutrition_plan(self, client, auth_headers):
        """POST /ai/nutrition-plan retorna metas nutricionais."""
        resp = await client.post(
            "/api/v1/ai/nutrition-plan",
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert "plan" in data
        assert data["plan"]["target_calories"] > 0
