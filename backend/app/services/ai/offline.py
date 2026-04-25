"""
IA Modo A — Heurísticas offline, zero custo.
Baseado em evidências científicas de treinamento e nutrição.
"""

import math
from typing import Any, Dict, List

from app.services.ai.base import BaseAIService


class OfflineAIService(BaseAIService):
    """
    Serviço de IA 100% offline usando heurísticas e templates determinísticos.
    Não requer nenhuma chave de API ou conexão externa.
    """

    # Splits de treino por frequência semanal
    SPLITS = {
        2: "Full Body",
        3: "Full Body A/B/C",
        4: "Upper/Lower",
        5: "PPL + 2x Full",
        6: "PPL",
        7: "PPL + Upper/Lower",
    }

    # Volume por grupo muscular (séries/semana) por nível
    VOLUME = {
        "iniciante": {"min": 10, "max": 12},
        "intermediario": {"min": 12, "max": 16},
        "avancado": {"min": 16, "max": 20},
    }

    # Exercícios base por grupo muscular
    EXERCISES = {
        "peito": [
            {"nome": "Supino Reto", "equipamento": "barra"},
            {"nome": "Supino Inclinado", "equipamento": "halteres"},
            {"nome": "Crucifixo", "equipamento": "halteres"},
            {"nome": "Crossover", "equipamento": "cabo"},
        ],
        "costas": [
            {"nome": "Barra Fixa", "equipamento": "barra"},
            {"nome": "Remada Curvada", "equipamento": "barra"},
            {"nome": "Puxada na Frente", "equipamento": "cabo"},
            {"nome": "Remada Unilateral", "equipamento": "halteres"},
        ],
        "ombros": [
            {"nome": "Desenvolvimento com Barra", "equipamento": "barra"},
            {"nome": "Elevação Lateral", "equipamento": "halteres"},
            {"nome": "Elevação Frontal", "equipamento": "halteres"},
        ],
        "biceps": [
            {"nome": "Rosca Direta", "equipamento": "barra"},
            {"nome": "Rosca Alternada", "equipamento": "halteres"},
            {"nome": "Rosca Concentrada", "equipamento": "halteres"},
        ],
        "triceps": [
            {"nome": "Tríceps Testa", "equipamento": "barra"},
            {"nome": "Tríceps Corda", "equipamento": "cabo"},
            {"nome": "Mergulho", "equipamento": "paralelas"},
        ],
        "quadriceps": [
            {"nome": "Agachamento", "equipamento": "barra"},
            {"nome": "Leg Press", "equipamento": "máquina"},
            {"nome": "Avanço", "equipamento": "halteres"},
        ],
        "posterior": [
            {"nome": "Levantamento Terra", "equipamento": "barra"},
            {"nome": "Mesa Flexora", "equipamento": "máquina"},
            {"nome": "Stiff", "equipamento": "barra"},
        ],
        "gluteos": [
            {"nome": "Hip Thrust", "equipamento": "barra"},
            {"nome": "Afundo", "equipamento": "halteres"},
        ],
        "abdomen": [
            {"nome": "Prancha", "equipamento": "peso_corporal"},
            {"nome": "Abdominal Supra", "equipamento": "peso_corporal"},
            {"nome": "Abdominal Infra", "equipamento": "peso_corporal"},
        ],
    }

    async def generate_workout_plan(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gera microciclo semanal baseado nos parâmetros do usuário.
        """
        goal = params.get("goal", "manutencao")
        frequency = params.get("weekly_frequency", 4)
        level = params.get("level", "iniciante")
        limitations = params.get("limitations", "")

        split = self.SPLITS.get(frequency, "Upper/Lower")
        volume = self.VOLUME[level]

        # Gerar dias de treino
        days = self._generate_days(frequency, level, goal)

        # Calcular progressão
        progression_pct = 2.5 if level == "iniciante" else (5.0 if level == "avancado" else 3.75)

        return {
            "ia_mode": "A",
            "split": split,
            "frequency": frequency,
            "level": level,
            "goal": goal,
            "weeks": 4,
            "deload_week": 4,
            "progression_percent": progression_pct,
            "weekly_volume_sets_per_muscle": volume,
            "days": days,
            "notes": self._get_notes(goal, level, limitations),
            "general_tips": [
                "Aqueça por 5-10 minutos antes de cada sessão",
                "Descanse 60-90 segundos entre séries para hipertrofia",
                "Descanse 2-3 minutos entre séries para força",
                "Durma 7-9 horas por noite para melhor recuperação",
                f"Aplique deload (reduzir carga 30-40%) na semana {4}",
            ],
        }

    def _generate_days(self, frequency: int, level: str, goal: str) -> List[Dict]:
        """Gera estrutura de dias de treino."""
        if frequency <= 3:
            return self._full_body_split(frequency, level)
        elif frequency == 4:
            return self._upper_lower_split(level)
        else:
            return self._ppl_split(frequency, level)

    def _full_body_split(self, frequency: int, level: str) -> List[Dict]:
        """Full Body para 2-3x/semana."""
        days = []
        day_names = ["Segunda-feira", "Quarta-feira", "Sexta-feira"][:frequency]

        for i, day_name in enumerate(day_names):
            exercises = []
            # Seleção balanceada de grupos musculares
            priority_groups = ["quadriceps", "costas", "peito", "ombros", "biceps", "triceps"]
            for group in priority_groups[:6]:
                ex_list = self.EXERCISES.get(group, [])
                if ex_list:
                    ex = ex_list[i % len(ex_list)]
                    sets = 3 if level == "iniciante" else 4
                    exercises.append({
                        "exercicio": ex["nome"],
                        "grupo_muscular": group,
                        "series": sets,
                        "reps": "8-12",
                        "equipamento": ex["equipamento"],
                        "descanso_segundos": 90,
                    })
            days.append({"dia": day_name, "tipo": "Full Body", "exercicios": exercises, "duracao_min": 60})

        return days

    def _upper_lower_split(self, level: str) -> List[Dict]:
        """Upper/Lower para 4x/semana."""
        sets = 3 if level == "iniciante" else 4

        upper = {
            "dia": "Segunda/Quinta-feira",
            "tipo": "Upper (Superior)",
            "exercicios": [
                {"exercicio": "Supino Reto", "grupo_muscular": "peito", "series": sets, "reps": "6-10", "equipamento": "barra", "descanso_segundos": 120},
                {"exercicio": "Remada Curvada", "grupo_muscular": "costas", "series": sets, "reps": "6-10", "equipamento": "barra", "descanso_segundos": 120},
                {"exercicio": "Desenvolvimento", "grupo_muscular": "ombros", "series": sets, "reps": "8-12", "equipamento": "halteres", "descanso_segundos": 90},
                {"exercicio": "Rosca Direta", "grupo_muscular": "biceps", "series": sets - 1, "reps": "10-15", "equipamento": "barra", "descanso_segundos": 60},
                {"exercicio": "Tríceps Corda", "grupo_muscular": "triceps", "series": sets - 1, "reps": "10-15", "equipamento": "cabo", "descanso_segundos": 60},
            ],
            "duracao_min": 60,
        }

        lower = {
            "dia": "Terça/Sexta-feira",
            "tipo": "Lower (Inferior)",
            "exercicios": [
                {"exercicio": "Agachamento", "grupo_muscular": "quadriceps", "series": sets, "reps": "6-10", "equipamento": "barra", "descanso_segundos": 180},
                {"exercicio": "Levantamento Terra", "grupo_muscular": "posterior", "series": sets, "reps": "5-8", "equipamento": "barra", "descanso_segundos": 180},
                {"exercicio": "Leg Press", "grupo_muscular": "quadriceps", "series": sets - 1, "reps": "10-15", "equipamento": "máquina", "descanso_segundos": 90},
                {"exercicio": "Mesa Flexora", "grupo_muscular": "posterior", "series": sets - 1, "reps": "10-15", "equipamento": "máquina", "descanso_segundos": 90},
                {"exercicio": "Panturrilha", "grupo_muscular": "panturrilha", "series": 4, "reps": "15-20", "equipamento": "máquina", "descanso_segundos": 60},
            ],
            "duracao_min": 65,
        }

        return [upper, lower]

    def _ppl_split(self, frequency: int, level: str) -> List[Dict]:
        """Push/Pull/Legs para 5-6x/semana."""
        sets = 4 if level in ("intermediario", "avancado") else 3

        push = {
            "dia": "Segunda/Quinta-feira",
            "tipo": "Push (Empurrar)",
            "exercicios": [
                {"exercicio": "Supino Reto", "grupo_muscular": "peito", "series": sets, "reps": "6-10", "equipamento": "barra", "descanso_segundos": 120},
                {"exercicio": "Supino Inclinado", "grupo_muscular": "peito", "series": sets - 1, "reps": "8-12", "equipamento": "halteres", "descanso_segundos": 90},
                {"exercicio": "Desenvolvimento", "grupo_muscular": "ombros", "series": sets, "reps": "8-12", "equipamento": "halteres", "descanso_segundos": 90},
                {"exercicio": "Elevação Lateral", "grupo_muscular": "ombros", "series": 3, "reps": "12-15", "equipamento": "halteres", "descanso_segundos": 60},
                {"exercicio": "Tríceps Testa", "grupo_muscular": "triceps", "series": 3, "reps": "10-15", "equipamento": "barra", "descanso_segundos": 60},
            ],
            "duracao_min": 65,
        }

        pull = {
            "dia": "Terça/Sexta-feira",
            "tipo": "Pull (Puxar)",
            "exercicios": [
                {"exercicio": "Barra Fixa", "grupo_muscular": "costas", "series": sets, "reps": "6-10", "equipamento": "barra", "descanso_segundos": 120},
                {"exercicio": "Remada Curvada", "grupo_muscular": "costas", "series": sets, "reps": "6-10", "equipamento": "barra", "descanso_segundos": 120},
                {"exercicio": "Puxada na Frente", "grupo_muscular": "costas", "series": sets - 1, "reps": "10-12", "equipamento": "cabo", "descanso_segundos": 90},
                {"exercicio": "Rosca Direta", "grupo_muscular": "biceps", "series": 3, "reps": "10-15", "equipamento": "barra", "descanso_segundos": 60},
                {"exercicio": "Rosca Martelo", "grupo_muscular": "biceps", "series": 3, "reps": "10-15", "equipamento": "halteres", "descanso_segundos": 60},
            ],
            "duracao_min": 65,
        }

        legs = {
            "dia": "Quarta/Sábado-feira",
            "tipo": "Legs (Pernas)",
            "exercicios": [
                {"exercicio": "Agachamento", "grupo_muscular": "quadriceps", "series": sets, "reps": "6-10", "equipamento": "barra", "descanso_segundos": 180},
                {"exercicio": "Leg Press", "grupo_muscular": "quadriceps", "series": sets - 1, "reps": "10-15", "equipamento": "máquina", "descanso_segundos": 90},
                {"exercicio": "Levantamento Terra", "grupo_muscular": "posterior", "series": sets, "reps": "6-8", "equipamento": "barra", "descanso_segundos": 180},
                {"exercicio": "Mesa Flexora", "grupo_muscular": "posterior", "series": 3, "reps": "12-15", "equipamento": "máquina", "descanso_segundos": 60},
                {"exercicio": "Hip Thrust", "grupo_muscular": "gluteos", "series": 3, "reps": "10-15", "equipamento": "barra", "descanso_segundos": 90},
            ],
            "duracao_min": 70,
        }

        days = [push, pull, legs]
        if frequency >= 6:
            days.extend([push.copy(), pull.copy(), legs.copy()])
        elif frequency == 5:
            days.extend([push.copy(), pull.copy()])

        return days[:frequency]

    def _get_notes(self, goal: str, level: str, limitations: str) -> str:
        notes = []
        if goal == "cutting":
            notes.append("Mantenha as cargas altas mesmo em déficit calórico para preservar massa muscular.")
        elif goal == "bulking":
            notes.append("Foque em sobrecarga progressiva para maximizar ganho de massa.")
        else:
            notes.append("Equilíbrio entre força e hipertrofia.")

        if level == "iniciante":
            notes.append("Como iniciante, você pode progredir em peso a cada sessão (progressão linear).")

        if limitations:
            notes.append(f"Atenção às limitações informadas: {limitations}. Consulte um profissional se necessário.")

        return " ".join(notes)

    async def generate_nutrition_plan(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gera plano nutricional usando Mifflin-St Jeor + ajuste por objetivo.
        """
        weight = params["weight_kg"]
        height = params["height_cm"]
        age = params["age"]
        goal = params["goal"]
        activity = params.get("activity_level", "moderado")
        gender = params.get("gender", "masculino")

        # TDEE via Mifflin-St Jeor
        if gender == "feminino":
            bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
        else:
            bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5

        # Fator de atividade
        activity_factors = {
            "sedentario": 1.2,
            "leve": 1.375,
            "moderado": 1.55,
            "ativo": 1.725,
            "muito_ativo": 1.9,
        }
        tdee = bmr * activity_factors.get(activity, 1.55)

        # Ajuste por objetivo
        if goal == "cutting":
            target_calories = tdee * 0.85
        elif goal == "bulking":
            target_calories = tdee * 1.10
        else:
            target_calories = tdee

        # Macros
        protein_g = weight * 2.0  # 2g/kg
        fat_g = (target_calories * 0.27) / 9  # 27% das calorias
        carbs_calories = target_calories - (protein_g * 4) - (fat_g * 9)
        carbs_g = max(0, carbs_calories / 4)

        return {
            "ia_mode": "A",
            "tdee": round(tdee),
            "target_calories": round(target_calories),
            "goal": goal,
            "macros": {
                "protein_g": round(protein_g),
                "carbs_g": round(carbs_g),
                "fat_g": round(fat_g),
            },
            "meal_distribution": self._get_meal_distribution(target_calories, protein_g, carbs_g, fat_g),
            "hydration_ml": round(weight * 35),  # 35ml/kg
            "tips": self._get_nutrition_tips(goal, weight),
        }

    def _get_meal_distribution(self, calories, protein, carbs, fat) -> List[Dict]:
        """Distribui macros em 4-5 refeições."""
        meals = [
            {"nome": "Café da manhã (7h)", "percentual": 0.25},
            {"nome": "Lanche da manhã (10h)", "percentual": 0.15},
            {"nome": "Almoço (12h-13h)", "percentual": 0.30},
            {"nome": "Lanche da tarde (16h)", "percentual": 0.15},
            {"nome": "Jantar (19h-20h)", "percentual": 0.15},
        ]
        return [
            {
                "refeicao": m["nome"],
                "calorias": round(calories * m["percentual"]),
                "proteina_g": round(protein * m["percentual"]),
                "carboidrato_g": round(carbs * m["percentual"]),
                "gordura_g": round(fat * m["percentual"]),
            }
            for m in meals
        ]

    def _get_nutrition_tips(self, goal: str, weight: float) -> List[str]:
        tips = [
            f"Beba pelo menos {round(weight * 35)}ml de água por dia.",
            "Priorize alimentos minimamente processados.",
            "Consuma proteína em todas as refeições.",
        ]
        if goal == "cutting":
            tips.extend([
                "Em déficit, mantenha proteína alta (2-2.2g/kg) para preservar músculo.",
                "Prefira alimentos de alto volume e baixa caloria (vegetais, proteínas magras).",
            ])
        elif goal == "bulking":
            tips.extend([
                "Comer em superávit pode ser desafiador — adicione carboidratos de qualidade.",
                "Pós-treino: 40-60g proteína + carboidratos para recuperação.",
            ])
        return tips

    async def analyze_progress(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa progresso usando médias móveis e regressão simples."""
        workouts = params.get("workouts", [])
        weights = params.get("body_weights", [])
        nutrition = params.get("nutrition", {})

        analysis = {
            "ia_mode": "A",
            "periodo_dias": params.get("days", 30),
            "insights": [],
            "recomendacoes": [],
        }

        # Análise de treinos
        if workouts:
            total = len(workouts)
            analysis["insights"].append(f"Você registrou {total} treinos no período.")

            # Grupos mais trabalhados
            groups = {}
            for w in workouts:
                g = w.get("muscle_group", "")
                groups[g] = groups.get(g, 0) + 1

            if groups:
                top = max(groups, key=groups.get)
                low = min(groups, key=groups.get)
                analysis["insights"].append(f"Grupo mais trabalhado: {top} ({groups[top]}x).")
                if groups[top] > groups[low] * 2:
                    analysis["recomendacoes"].append(
                        f"Considere aumentar o volume para {low} para maior equilíbrio muscular."
                    )

        # Análise de peso corporal
        if len(weights) >= 7:
            first_week = sum(weights[:7]) / 7
            last_week = sum(weights[-7:]) / 7
            diff = last_week - first_week
            analysis["insights"].append(
                f"Variação de peso (média móvel 7 dias): {diff:+.1f}kg"
            )

        # Aderência nutricional
        if nutrition:
            adherence = nutrition.get("adherence_pct", 0)
            analysis["insights"].append(f"Aderência calórica: {adherence:.0f}%")
            if adherence < 80:
                analysis["recomendacoes"].append(
                    "Aderência nutricional abaixo de 80%. Considere simplificar o plano alimentar."
                )

        if not analysis["recomendacoes"]:
            analysis["recomendacoes"].append("Continue com o plano atual — você está indo bem!")

        return analysis
