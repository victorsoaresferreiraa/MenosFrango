"""
IA Modo A — Heurísticas offline determinísticas.
Não requer API externa nem GPU. Funciona 100% sem internet.
"""

from typing import Any

# ─── Tabelas de configuração ────────────────────────────────────

SPLITS = {
    3: {
        "nome": "Full Body 3x",
        "dias": [
            {"dia": 1, "foco": "Full Body A", "grupos": ["peito", "costas", "pernas", "ombro"]},
            {"dia": 3, "foco": "Full Body B", "grupos": ["peito", "costas", "pernas", "bracos"]},
            {"dia": 5, "foco": "Full Body C", "grupos": ["peito", "costas", "pernas", "ombro", "bracos"]},
        ],
    },
    4: {
        "nome": "Upper/Lower 4x",
        "dias": [
            {"dia": 1, "foco": "Upper A (Push)", "grupos": ["peito", "ombro", "triceps"]},
            {"dia": 2, "foco": "Lower A", "grupos": ["quadriceps", "posterior", "gluteos"]},
            {"dia": 4, "foco": "Upper B (Pull)", "grupos": ["costas", "biceps", "trapezio"]},
            {"dia": 5, "foco": "Lower B", "grupos": ["quadriceps", "posterior", "panturrilha"]},
        ],
    },
    5: {
        "nome": "PPL 5x",
        "dias": [
            {"dia": 1, "foco": "Push", "grupos": ["peito", "ombro", "triceps"]},
            {"dia": 2, "foco": "Pull", "grupos": ["costas", "biceps", "trapezio"]},
            {"dia": 3, "foco": "Legs", "grupos": ["quadriceps", "posterior", "gluteos"]},
            {"dia": 5, "foco": "Push", "grupos": ["peito", "ombro", "triceps"]},
            {"dia": 6, "foco": "Pull", "grupos": ["costas", "biceps"]},
        ],
    },
    6: {
        "nome": "PPL 6x",
        "dias": [
            {"dia": 1, "foco": "Push", "grupos": ["peito", "ombro", "triceps"]},
            {"dia": 2, "foco": "Pull", "grupos": ["costas", "biceps", "trapezio"]},
            {"dia": 3, "foco": "Legs", "grupos": ["quadriceps", "posterior", "gluteos"]},
            {"dia": 4, "foco": "Push", "grupos": ["peito", "ombro", "triceps"]},
            {"dia": 5, "foco": "Pull", "grupos": ["costas", "biceps"]},
            {"dia": 6, "foco": "Legs", "grupos": ["quadriceps", "posterior", "panturrilha"]},
        ],
    },
}

EXERCICIOS_POR_GRUPO = {
    "peito": ["Supino Reto", "Supino Inclinado", "Crucifixo", "Flexão de Braços", "Peck Deck"],
    "costas": ["Puxada Frontal", "Remada Curvada", "Remada Unilateral", "Levantamento Terra", "Pullover"],
    "ombro": ["Desenvolvimento", "Elevação Lateral", "Elevação Frontal", "Desenvolvimento Arnold", "Face Pull"],
    "triceps": ["Tríceps Pulley", "Tríceps Testa", "Mergulho", "Tríceps Coice", "Extensão Unilateral"],
    "biceps": ["Rosca Direta", "Rosca Martelo", "Rosca Inclinada", "Rosca Concentrada", "Rosca Scott"],
    "trapezio": ["Encolhimento", "Remada Alta", "Elevação com Halteres"],
    "quadriceps": ["Agachamento", "Leg Press", "Extensora", "Afundo", "Hack Squat"],
    "posterior": ["Mesa Flexora", "Stiff", "Cadeira Flexora", "Levantamento Terra Romano"],
    "gluteos": ["Agachamento Sumô", "Hip Thrust", "Glúteo no Cabo", "Afundo Reverso"],
    "panturrilha": ["Panturrilha em Pé", "Panturrilha Sentado", "Leg Press Panturrilha"],
    "bracos": ["Rosca Direta", "Tríceps Pulley", "Rosca Martelo", "Mergulho"],
    "abdomen": ["Abdominal Crunch", "Plank", "Abdominal Infra", "Abdominal Oblíquo"],
}

SERIES_POR_NIVEL = {
    "iniciante": {"series": 3, "reps_forca": "6-8", "reps_hipert": "10-12", "reps_resist": "15-20"},
    "intermediario": {"series": 4, "reps_forca": "5-7", "reps_hipert": "8-12", "reps_resist": "12-15"},
    "avancado": {"series": 4, "reps_forca": "3-6", "reps_hipert": "6-10", "reps_resist": "10-15"},
}


def calcular_tdee(peso: float, altura: float, idade: int, sexo: str = "M") -> float:
    """Mifflin-St Jeor para TDEE com fator de atividade moderado."""
    if sexo == "M":
        tmb = 10 * peso + 6.25 * altura - 5 * idade + 5
    else:
        tmb = 10 * peso + 6.25 * altura - 5 * idade - 161
    return tmb * 1.55  # atividade moderada


def gerar_plano_treino(
    objetivo: str,
    frequencia_semanal: int,
    nivel: str,
    limitacoes: list[str] | None = None,
) -> dict[str, Any]:
    """
    Gera microciclo semanal com progressão linear e semanas de deload.

    Args:
        objetivo: cutting|bulking|manutencao
        frequencia_semanal: 3-6 dias por semana
        nivel: iniciante|intermediario|avancado
        limitacoes: grupos musculares a evitar

    Returns:
        Plano estruturado com exercícios, séries, reps e progressão.
    """
    freq = max(3, min(6, frequencia_semanal))
    split = SPLITS.get(freq, SPLITS[4])
    config = SERIES_POR_NIVEL.get(nivel, SERIES_POR_NIVEL["iniciante"])
    limitacoes = limitacoes or []

    dias_treino = []
    for dia_config in split["dias"]:
        exercicios = []
        for grupo in dia_config["grupos"]:
            if grupo in limitacoes:
                continue
            lista = EXERCICIOS_POR_GRUPO.get(grupo, [])
            if lista:
                # Escolhe os 2 primeiros exercícios de cada grupo
                for exercicio in lista[:2]:
                    exercicios.append({
                        "exercicio": exercicio,
                        "grupo_muscular": grupo,
                        "series": config["series"],
                        "reps": config["reps_hipert"],
                        "descanso_seg": 90,
                    })

        dias_treino.append({
            "dia": dia_config["dia"],
            "foco": dia_config["foco"],
            "exercicios": exercicios,
        })

    # Progressão linear
    progressao = {
        "tipo": "progressão linear",
        "incremento_kg": 2.5 if nivel == "iniciante" else 1.25,
        "frequencia": "a cada sessão bem-sucedida",
        "deload": "a cada 4-6 semanas, reduzir carga 10-15%",
    }

    # Ajuste por objetivo
    observacoes = []
    if objetivo == "cutting":
        observacoes.append("Volume ligeiramente reduzido; priorize intensidade para reter massa.")
        observacoes.append("Descanso encurtado (60-75s) para maior gasto calórico.")
    elif objetivo == "bulking":
        observacoes.append("Foco em carga progressiva; descanso 90-120s.")
        observacoes.append("Adicione 1 série extra por grupo a cada 2 semanas.")
    else:
        observacoes.append("Manutenção: equilíbrio entre volume e intensidade.")

    return {
        "split": split["nome"],
        "frequencia_semanal": freq,
        "nivel": nivel,
        "objetivo": objetivo,
        "dias": dias_treino,
        "progressao": progressao,
        "observacoes": observacoes,
        "gerado_por": "Athletic AI Modo A (offline)",
    }


def gerar_plano_nutricional(
    peso: float,
    altura: float,
    idade: int,
    objetivo: str,
    sexo: str = "M",
) -> dict[str, Any]:
    """
    Gera plano nutricional baseado em TDEE com macros ajustados por objetivo.

    Proteína: 1.6–2.2g/kg
    Gordura: 25–30% das calorias
    Carbo: restante
    """
    tdee = calcular_tdee(peso, altura, idade, sexo)

    if objetivo == "cutting":
        calorias_alvo = tdee * 0.85  # déficit 15%
        proteina_g = peso * 2.2
        descricao_objetivo = "Déficit calórico de 15% para redução de gordura"
    elif objetivo == "bulking":
        calorias_alvo = tdee * 1.10  # superávit 10%
        proteina_g = peso * 1.8
        descricao_objetivo = "Superávit calórico de 10% para ganho de massa"
    else:
        calorias_alvo = tdee
        proteina_g = peso * 1.6
        descricao_objetivo = "Calorias de manutenção"

    gordura_g = (calorias_alvo * 0.27) / 9
    proteina_kcal = proteina_g * 4
    gordura_kcal = gordura_g * 9
    carbo_kcal = calorias_alvo - proteina_kcal - gordura_kcal
    carbo_g = carbo_kcal / 4

    return {
        "tdee": round(tdee),
        "calorias_alvo": round(calorias_alvo),
        "descricao_objetivo": descricao_objetivo,
        "macros": {
            "proteinas_g": round(proteina_g),
            "carboidratos_g": round(carbo_g),
            "gorduras_g": round(gordura_g),
            "proteinas_pct": round(proteina_kcal / calorias_alvo * 100),
            "carboidratos_pct": round(carbo_kcal / calorias_alvo * 100),
            "gorduras_pct": round(gordura_kcal / calorias_alvo * 100),
        },
        "refeicoes_sugeridas": 4,
        "dicas": [
            f"Consuma {round(proteina_g)}g de proteína distribuída em {4} refeições",
            "Prefira carboidratos complexos (aveia, batata doce, arroz integral)",
            "Inclua gorduras saudáveis (azeite, abacate, castanhas)",
            "Hidrate-se: 35ml × peso corporal = ml de água/dia",
        ],
        "gerado_por": "Athletic AI Modo A (offline)",
    }


def analisar_progresso(
    historico_pesos: list[float],
    historico_volumes: list[float],
) -> dict[str, Any]:
    """
    Analisa progresso com média móvel 7 dias e regressão linear simples.
    Retorna ajustes recomendados (±5%).
    """
    def media_movel(valores: list[float], janela: int = 7) -> list[float]:
        result = []
        for i in range(len(valores)):
            inicio = max(0, i - janela + 1)
            result.append(sum(valores[inicio:i+1]) / (i - inicio + 1))
        return result

    def regressao_linear(y: list[float]) -> tuple[float, float]:
        """Retorna (inclinação, intercepto) por mínimos quadrados."""
        n = len(y)
        if n < 2:
            return 0.0, y[0] if y else 0.0
        x_mean = (n - 1) / 2
        y_mean = sum(y) / n
        numerador = sum((i - x_mean) * (y[i] - y_mean) for i in range(n))
        denominador = sum((i - x_mean) ** 2 for i in range(n))
        slope = numerador / denominador if denominador != 0 else 0.0
        intercept = y_mean - slope * x_mean
        return slope, intercept

    recomendacoes = []
    tendencia_peso = "estável"
    tendencia_volume = "estável"

    if len(historico_pesos) >= 3:
        mm_peso = media_movel(historico_pesos)
        slope_peso, _ = regressao_linear(historico_pesos)
        if slope_peso < -0.1:
            tendencia_peso = "reduzindo"
            recomendacoes.append("Peso reduzindo consistentemente — objetivo de cutting em curso.")
        elif slope_peso > 0.1:
            tendencia_peso = "aumentando"
            recomendacoes.append("Peso aumentando — adequado para bulking.")

    if len(historico_volumes) >= 3:
        slope_vol, _ = regressao_linear(historico_volumes)
        if slope_vol > 0:
            tendencia_volume = "aumentando"
            recomendacoes.append("Volume de treino crescendo — excelente progressão!")
        elif slope_vol < -0.05:
            tendencia_volume = "reduzindo"
            recomendacoes.append("Volume reduzindo — considere aumentar carga ou séries em +5%.")

    return {
        "tendencia_peso": tendencia_peso,
        "tendencia_volume": tendencia_volume,
        "recomendacoes": recomendacoes or ["Continue com o plano atual — progresso estável."],
        "ajuste_sugerido_pct": 5 if tendencia_volume == "reduzindo" else 0,
        "gerado_por": "Athletic AI Modo A (offline)",
    }
