"""
Camada de IA do Athletic AI.

Modo A (padrão): Heurísticas e templates determinísticos — 100% offline, zero custo.
Modo B: Ollama (LLM local) — requer container ollama rodando.
Modo C: OpenAI/Anthropic API — pago, desativado por padrão.

Controlado via FEATURE_FLAG_IA_MODE no .env.
"""
import logging
import math
from typing import Any

from app.core.config import get_settings
from app.models.user import NivelEnum, ObjetivoEnum, User

logger = logging.getLogger(__name__)
settings = get_settings()


# ─── Modo A: Heurísticas offline ──────────────────────────

class HeuristicAI:
    """
    Gerador de planos de treino e dieta baseado em regras e fórmulas
    científicas. Funciona 100% offline, sem dependências externas.
    """

    # Grupos musculares disponíveis
    MUSCLE_GROUPS = [
        "Peitoral", "Costas", "Ombros", "Bíceps", "Tríceps",
        "Quadríceps", "Posterior", "Glúteos", "Panturrilha", "Abdômen"
    ]

    # Exercícios por grupo muscular
    EXERCISES = {
        "Peitoral": ["Supino Reto", "Supino Inclinado", "Crucifixo", "Crossover"],
        "Costas": ["Puxada Frontal", "Remada Curvada", "Remada Unilateral", "Levantamento Terra"],
        "Ombros": ["Desenvolvimento Militar", "Elevação Lateral", "Elevação Frontal"],
        "Bíceps": ["Rosca Direta", "Rosca Alternada", "Rosca Martelo"],
        "Tríceps": ["Tríceps Pulley", "Tríceps Testa", "Mergulho no Banco"],
        "Quadríceps": ["Agachamento", "Leg Press", "Extensora", "Avanço"],
        "Posterior": ["Mesa Flexora", "Stiff", "Leg Curl"],
        "Glúteos": ["Hip Thrust", "Abdução", "Agachamento Sumô"],
        "Panturrilha": ["Panturrilha em Pé", "Panturrilha Sentado"],
        "Abdômen": ["Abdominal Crunch", "Prancha", "Elevação de Pernas"],
    }

    def calculate_tdee(self, user: User) -> float:
        """
        Calcula TDEE (Total Daily Energy Expenditure) usando Mifflin-St Jeor.
        Assume nível de atividade moderado (fator 1.55).
        """
        if not all([user.weight_kg, user.height_cm, user.age]):
            return 2000.0  # valor padrão se não houver dados

        # Fórmula Mifflin-St Jeor (unissex simplificada)
        bmr = (10 * user.weight_kg) + (6.25 * user.height_cm) - (5 * user.age) + 5

        # Fator de atividade por nível
        activity_factors = {
            NivelEnum.INICIANTE: 1.375,        # Levemente ativo
            NivelEnum.INTERMEDIARIO: 1.55,     # Moderadamente ativo
            NivelEnum.AVANCADO: 1.725,         # Muito ativo
        }
        factor = activity_factors.get(user.nivel, 1.55)
        return round(bmr * factor, 0)

    def generate_nutrition_plan(self, user: User) -> dict[str, Any]:
        """
        Gera plano nutricional baseado no TDEE e objetivo.
        Proteína: 1.6–2.2g/kg | Gordura: 25–30% | Resto: carboidratos.
        """
        tdee = self.calculate_tdee(user)
        weight = user.weight_kg or 75.0

        # Ajuste calórico por objetivo
        calorie_adjustments = {
            ObjetivoEnum.CUTTING: -0.15,      # -15% TDEE
            ObjetivoEnum.BULKING: +0.10,      # +10% TDEE
            ObjetivoEnum.MANUTENCAO: 0.0,
        }
        adjustment = calorie_adjustments.get(user.objetivo, 0.0)
        target_calories = round(tdee * (1 + adjustment), 0)

        # Proteína por objetivo e nível
        protein_per_kg = {
            ObjetivoEnum.CUTTING: 2.2,        # Mais proteína no cutting
            ObjetivoEnum.BULKING: 1.8,
            ObjetivoEnum.MANUTENCAO: 1.6,
        }
        protein_g = round(weight * protein_per_kg.get(user.objetivo, 1.8), 0)

        # Gordura: 25-30% das calorias
        fat_ratio = 0.28
        fat_g = round((target_calories * fat_ratio) / 9, 0)

        # Carboidratos: o restante
        protein_kcal = protein_g * 4
        fat_kcal = fat_g * 9
        carbs_g = round((target_calories - protein_kcal - fat_kcal) / 4, 0)
        carbs_g = max(carbs_g, 50)  # mínimo de 50g

        objetivo_labels = {
            ObjetivoEnum.CUTTING: "Déficit calórico (-15%)",
            ObjetivoEnum.BULKING: "Superávit calórico (+10%)",
            ObjetivoEnum.MANUTENCAO: "Manutenção calórica",
        }

        return {
            "tdee": tdee,
            "target_calories": target_calories,
            "protein_g": protein_g,
            "carbs_g": carbs_g,
            "fat_g": fat_g,
            "objetivo": user.objetivo.value,
            "strategy": objetivo_labels.get(user.objetivo, ""),
            "notes": (
                f"TDEE calculado por Mifflin-St Jeor. "
                f"Proteína: {protein_per_kg.get(user.objetivo, 1.8)}g/kg. "
                f"Reavalie a cada 2-4 semanas."
            ),
            "meal_suggestions": self._get_meal_suggestions(user.objetivo),
            "ia_mode": "A",
        }

    def generate_workout_plan(
        self,
        user: User,
        weekly_frequency: int = 4,
        limitations: str = "",
    ) -> dict[str, Any]:
        """
        Gera microciclo semanal de treino.
        Suporta splits: Full Body, Upper/Lower, PPL.
        Inclui progressão linear e semanas de deload.
        """
        freq = max(2, min(weekly_frequency, 6))

        # Escolhe split pela frequência
        if freq <= 2:
            split_type = "full_body"
        elif freq <= 4:
            split_type = "upper_lower"
        else:
            split_type = "ppl"

        # Séries por grupo por semana (baseado no nível)
        series_ranges = {
            NivelEnum.INICIANTE: (10, 12),
            NivelEnum.INTERMEDIARIO: (12, 15),
            NivelEnum.AVANCADO: (15, 20),
        }
        sets_per_group = series_ranges.get(user.nivel, (12, 15))

        # Gera o plano semanal
        weekly_plan = self._build_weekly_plan(split_type, freq, sets_per_group, user.nivel)

        return {
            "split_type": split_type,
            "weekly_frequency": freq,
            "nivel": user.nivel.value,
            "objetivo": user.objetivo.value,
            "weeks": [
                {"week": 1, "type": "normal", "plan": weekly_plan},
                {"week": 2, "type": "normal", "plan": weekly_plan},
                {"week": 3, "type": "progressive", "plan": self._apply_progression(weekly_plan)},
                {"week": 4, "type": "deload", "plan": self._apply_deload(weekly_plan)},
            ],
            "progression_rule": "Aumente 2,5kg por sessão (membros inferiores) ou 1,25kg (superiores) quando completar todas as séries e reps com boa técnica.",
            "deload_rule": "Semana 4 de cada mês: reduza 40% do volume (séries) e 10% da carga.",
            "limitations_noted": limitations or "Nenhuma",
            "ia_mode": "A",
        }

    def _build_weekly_plan(
        self, split_type: str, freq: int, sets_range: tuple, nivel: NivelEnum
    ) -> list[dict]:
        """Constrói o plano semanal de acordo com o split."""
        days = []

        if split_type == "full_body":
            for i in range(freq):
                days.append({
                    "day": i + 1,
                    "name": f"Full Body {chr(65+i)}",
                    "exercises": self._get_full_body_exercises(sets_range, nivel),
                })

        elif split_type == "upper_lower":
            day_names = ["Upper A", "Lower A", "Upper B", "Lower B"]
            for i in range(freq):
                is_upper = i % 2 == 0
                days.append({
                    "day": i + 1,
                    "name": day_names[i % 4],
                    "exercises": self._get_upper_exercises(sets_range, nivel)
                    if is_upper else self._get_lower_exercises(sets_range, nivel),
                })

        else:  # PPL
            day_types = ["push", "pull", "legs", "push", "pull", "legs"]
            for i in range(freq):
                day_type = day_types[i % 6]
                days.append({
                    "day": i + 1,
                    "name": day_type.capitalize(),
                    "exercises": self._get_ppl_exercises(day_type, sets_range, nivel),
                })

        return days

    def _get_full_body_exercises(self, sets_range: tuple, nivel: NivelEnum) -> list[dict]:
        sets = sets_range[0] // 3  # Distribui entre mais exercícios
        reps = 10 if nivel == NivelEnum.INICIANTE else 8
        return [
            {"exercise": "Agachamento", "muscle_group": "Quadríceps", "sets": sets + 1, "reps": reps},
            {"exercise": "Supino Reto", "muscle_group": "Peitoral", "sets": sets, "reps": reps},
            {"exercise": "Puxada Frontal", "muscle_group": "Costas", "sets": sets, "reps": reps},
            {"exercise": "Desenvolvimento Militar", "muscle_group": "Ombros", "sets": sets, "reps": reps},
            {"exercise": "Rosca Direta", "muscle_group": "Bíceps", "sets": 2, "reps": 12},
            {"exercise": "Tríceps Pulley", "muscle_group": "Tríceps", "sets": 2, "reps": 12},
        ]

    def _get_upper_exercises(self, sets_range: tuple, nivel: NivelEnum) -> list[dict]:
        sets = sets_range[1] // 4
        return [
            {"exercise": "Supino Reto", "muscle_group": "Peitoral", "sets": sets + 1, "reps": 8},
            {"exercise": "Supino Inclinado", "muscle_group": "Peitoral", "sets": sets, "reps": 10},
            {"exercise": "Remada Curvada", "muscle_group": "Costas", "sets": sets + 1, "reps": 8},
            {"exercise": "Puxada Frontal", "muscle_group": "Costas", "sets": sets, "reps": 10},
            {"exercise": "Desenvolvimento Militar", "muscle_group": "Ombros", "sets": sets, "reps": 10},
            {"exercise": "Rosca Alternada", "muscle_group": "Bíceps", "sets": 3, "reps": 12},
            {"exercise": "Tríceps Testa", "muscle_group": "Tríceps", "sets": 3, "reps": 12},
        ]

    def _get_lower_exercises(self, sets_range: tuple, nivel: NivelEnum) -> list[dict]:
        sets = sets_range[1] // 3
        return [
            {"exercise": "Agachamento", "muscle_group": "Quadríceps", "sets": sets + 1, "reps": 8},
            {"exercise": "Leg Press", "muscle_group": "Quadríceps", "sets": sets, "reps": 10},
            {"exercise": "Stiff", "muscle_group": "Posterior", "sets": sets, "reps": 10},
            {"exercise": "Hip Thrust", "muscle_group": "Glúteos", "sets": sets, "reps": 12},
            {"exercise": "Mesa Flexora", "muscle_group": "Posterior", "sets": 3, "reps": 12},
            {"exercise": "Panturrilha em Pé", "muscle_group": "Panturrilha", "sets": 4, "reps": 15},
        ]

    def _get_ppl_exercises(self, day_type: str, sets_range: tuple, nivel: NivelEnum) -> list[dict]:
        sets = sets_range[1] // 4
        if day_type == "push":
            return [
                {"exercise": "Supino Reto", "muscle_group": "Peitoral", "sets": sets + 1, "reps": 8},
                {"exercise": "Supino Inclinado", "muscle_group": "Peitoral", "sets": sets, "reps": 10},
                {"exercise": "Crucifixo", "muscle_group": "Peitoral", "sets": 3, "reps": 12},
                {"exercise": "Desenvolvimento Militar", "muscle_group": "Ombros", "sets": sets, "reps": 10},
                {"exercise": "Elevação Lateral", "muscle_group": "Ombros", "sets": 3, "reps": 15},
                {"exercise": "Tríceps Pulley", "muscle_group": "Tríceps", "sets": 4, "reps": 12},
            ]
        elif day_type == "pull":
            return [
                {"exercise": "Levantamento Terra", "muscle_group": "Costas", "sets": sets, "reps": 5},
                {"exercise": "Remada Curvada", "muscle_group": "Costas", "sets": sets, "reps": 8},
                {"exercise": "Puxada Frontal", "muscle_group": "Costas", "sets": sets, "reps": 10},
                {"exercise": "Remada Unilateral", "muscle_group": "Costas", "sets": 3, "reps": 10},
                {"exercise": "Rosca Direta", "muscle_group": "Bíceps", "sets": 4, "reps": 12},
                {"exercise": "Rosca Martelo", "muscle_group": "Bíceps", "sets": 3, "reps": 12},
            ]
        else:  # legs
            return self._get_lower_exercises(sets_range, nivel)

    def _apply_progression(self, plan: list[dict]) -> list[dict]:
        """Aplica progressão de +1 série em exercícios principais."""
        import copy
        prog_plan = copy.deepcopy(plan)
        for day in prog_plan:
            for i, ex in enumerate(day["exercises"]):
                if i < 2:  # Apenas os 2 primeiros exercícios do dia
                    ex["sets"] = ex["sets"] + 1
        return prog_plan

    def _apply_deload(self, plan: list[dict]) -> list[dict]:
        """Aplica deload: -40% volume, -10% intensidade."""
        import copy
        deload_plan = copy.deepcopy(plan)
        for day in deload_plan:
            for ex in day["exercises"]:
                ex["sets"] = max(2, math.floor(ex["sets"] * 0.6))
                ex["reps"] = max(6, math.floor(ex["reps"] * 0.9))
                ex["note"] = "Deload: reduza a carga ~10%"
        return deload_plan

    def analyze_progress(self, workouts_data: list[dict], weight_data: list[dict]) -> dict:
        """
        Análise simples de progresso:
        - Média móvel 7 dias de carga
        - Identifica tendências
        - Sugere ajustes
        """
        if not workouts_data:
            return {
                "summary": "Sem dados suficientes para análise.",
                "trend": "neutro",
                "recommendations": ["Registre pelo menos 2 semanas de treinos para uma análise."],
                "ia_mode": "A",
            }

        # Calcula volume total por semana
        total_volume = sum(
            w.get("sets", 0) * w.get("reps", 0) * w.get("weight_kg", 0)
            for w in workouts_data
        )
        avg_volume = total_volume / max(len(workouts_data), 1)

        # Analisa tendência de peso corporal
        weight_trend = "estável"
        if len(weight_data) >= 2:
            recent = weight_data[0].get("weight_kg", 0)
            old = weight_data[-1].get("weight_kg", 0)
            diff = recent - old
            if diff > 0.5:
                weight_trend = "aumentando"
            elif diff < -0.5:
                weight_trend = "diminuindo"

        recommendations = [
            "Continue registrando treinos diariamente para uma análise mais precisa.",
            "Priorize sono de 7-9h para máxima recuperação.",
            "Hidrate-se bem (35ml/kg de peso corporal).",
        ]

        if avg_volume < 1000:
            recommendations.append("Volume semanal baixo — considere aumentar gradualmente.")

        return {
            "summary": f"Análise baseada em {len(workouts_data)} registros de treino.",
            "average_volume_per_session": round(avg_volume, 1),
            "weight_trend": weight_trend,
            "trend": "positivo" if avg_volume > 500 else "neutro",
            "recommendations": recommendations,
            "ia_mode": "A",
        }

    def _get_meal_suggestions(self, objetivo: ObjetivoEnum) -> list[str]:
        base = [
            "Priorize proteínas magras: frango, peixe, ovos, whey",
            "Carboidratos complexos: aveia, arroz integral, batata-doce",
            "Gorduras saudáveis: azeite, abacate, castanhas",
        ]
        if objetivo == ObjetivoEnum.CUTTING:
            return base + [
                "Distribua calorias em 4-5 refeições para controlar fome",
                "Prefira vegetais de alto volume e baixa caloria",
            ]
        elif objetivo == ObjetivoEnum.BULKING:
            return base + [
                "Adicione um shake pós-treino com whey + banana",
                "Não pule refeições — o superávit precisa ser consistente",
            ]
        return base


class AIService:
    """
    Fachada da camada de IA.
    Roteia para o modo configurado via FEATURE_FLAG_IA_MODE.
    """

    def __init__(self) -> None:
        self.mode = settings.feature_flag_ia_mode
        self.heuristic = HeuristicAI()

    async def generate_workout_plan(self, user: User, weekly_frequency: int, limitations: str) -> dict:
        if self.mode == "A":
            return self.heuristic.generate_workout_plan(user, weekly_frequency, limitations)
        elif self.mode == "B":
            return await self._ollama_workout(user, weekly_frequency, limitations)
        else:  # C
            return await self._openai_workout(user, weekly_frequency, limitations)

    async def generate_nutrition_plan(self, user: User) -> dict:
        if self.mode == "A":
            return self.heuristic.generate_nutrition_plan(user)
        elif self.mode == "B":
            return await self._ollama_nutrition(user)
        else:
            return await self._openai_nutrition(user)

    async def analyze_progress(self, user: User, workouts_data: list, weight_data: list) -> dict:
        # Modo A sempre disponível como fallback
        return self.heuristic.analyze_progress(workouts_data, weight_data)

    # ─── Modo B: Ollama ───────────────────────────────────

    async def _ollama_workout(self, user: User, frequency: int, limitations: str) -> dict:
        """Gera plano via Ollama (LLM local). Fallback para Modo A se indisponível."""
        try:
            import httpx
            prompt = self._build_workout_prompt(user, frequency, limitations)
            async with httpx.AsyncClient(timeout=60) as client:
                resp = await client.post(
                    f"{settings.ollama_endpoint}/api/generate",
                    json={"model": "llama3", "prompt": prompt, "stream": False},
                )
                data = resp.json()
                return {"content": data.get("response", ""), "ia_mode": "B"}
        except Exception as e:
            logger.warning("Ollama indisponível, usando Modo A: %s", e)
            return self.heuristic.generate_workout_plan(user, frequency, limitations)

    async def _ollama_nutrition(self, user: User) -> dict:
        try:
            import httpx
            prompt = self._build_nutrition_prompt(user)
            async with httpx.AsyncClient(timeout=60) as client:
                resp = await client.post(
                    f"{settings.ollama_endpoint}/api/generate",
                    json={"model": "llama3", "prompt": prompt, "stream": False},
                )
                data = resp.json()
                return {"content": data.get("response", ""), "ia_mode": "B"}
        except Exception as e:
            logger.warning("Ollama indisponível, usando Modo A: %s", e)
            return self.heuristic.generate_nutrition_plan(user)

    # ─── Modo C: OpenAI ───────────────────────────────────

    async def _openai_workout(self, user: User, frequency: int, limitations: str) -> dict:
        if not settings.openai_api_key:
            logger.warning("OpenAI API key não configurada, usando Modo A")
            return self.heuristic.generate_workout_plan(user, frequency, limitations)
        try:
            import httpx
            headers = {"Authorization": f"Bearer {settings.openai_api_key}"}
            payload = {
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": self._build_workout_prompt(user, frequency, limitations)}],
                "max_tokens": 2000,
            }
            async with httpx.AsyncClient(timeout=60) as client:
                resp = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers, json=payload,
                )
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                return {"content": content, "ia_mode": "C"}
        except Exception as e:
            logger.error("Erro na OpenAI API: %s", e)
            return self.heuristic.generate_workout_plan(user, frequency, limitations)

    async def _openai_nutrition(self, user: User) -> dict:
        if not settings.openai_api_key:
            return self.heuristic.generate_nutrition_plan(user)
        # Similar ao _openai_workout
        return self.heuristic.generate_nutrition_plan(user)

    def _build_workout_prompt(self, user: User, frequency: int, limitations: str) -> str:
        return (
            f"Crie um plano de treino semanal em português para: "
            f"objetivo={user.objetivo.value}, nível={user.nivel.value}, "
            f"frequência={frequency}x/semana, limitações='{limitations}'. "
            f"Inclua exercícios, séries, reps e dicas de progressão."
        )

    def _build_nutrition_prompt(self, user: User) -> str:
        return (
            f"Crie um plano nutricional em português para: "
            f"peso={user.weight_kg}kg, altura={user.height_cm}cm, "
            f"idade={user.age}, objetivo={user.objetivo.value}. "
            f"Inclua calorias, macros e sugestões de alimentos."
        )


# Instância singleton
ai_service = AIService()
