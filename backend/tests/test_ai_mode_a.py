"""Testes da IA Modo A (offline)."""

import pytest
from app.services.ai.mode_a import (
    gerar_plano_treino,
    gerar_plano_nutricional,
    analisar_progresso,
    calcular_tdee,
)


def test_tdee_masculino():
    """TDEE masculino calculado corretamente."""
    tdee = calcular_tdee(80, 175, 25, "M")
    assert 2500 < tdee < 3500


def test_plano_treino_3x():
    """Plano 3x por semana gera 3 dias."""
    plano = gerar_plano_treino("bulking", 3, "iniciante")
    assert len(plano["dias"]) == 3
    assert plano["nivel"] == "iniciante"
    assert plano["objetivo"] == "bulking"


def test_plano_treino_5x():
    """Plano 5x por semana gera 5 dias."""
    plano = gerar_plano_treino("cutting", 5, "avancado")
    assert len(plano["dias"]) == 5


def test_plano_treino_com_limitacoes():
    """Limitações removem grupos musculares."""
    plano = gerar_plano_treino("manutencao", 4, "intermediario", limitacoes=["peito"])
    for dia in plano["dias"]:
        for ex in dia["exercicios"]:
            assert ex["grupo_muscular"] != "peito"


def test_plano_nutricional_cutting():
    """Cutting aplica déficit de 15%."""
    plano = gerar_plano_nutricional(80, 175, 25, "cutting")
    tdee = plano["tdee"]
    alvo = plano["calorias_alvo"]
    assert abs(alvo - tdee * 0.85) < 5  # tolerância de arredondamento


def test_plano_nutricional_bulking():
    """Bulking aplica superávit de 10%."""
    plano = gerar_plano_nutricional(80, 175, 25, "bulking")
    assert plano["calorias_alvo"] > plano["tdee"]


def test_plano_nutricional_macros():
    """Macros somam aproximadamente às calorias alvo."""
    plano = gerar_plano_nutricional(80, 175, 25, "manutencao")
    macros = plano["macros"]
    cal_calculadas = (
        macros["proteinas_g"] * 4
        + macros["carboidratos_g"] * 4
        + macros["gorduras_g"] * 9
    )
    assert abs(cal_calculadas - plano["calorias_alvo"]) < 50


def test_analise_progresso_crescimento():
    """Volume crescendo gera recomendação positiva."""
    resultado = analisar_progresso(
        historico_pesos=[80, 80.5, 81, 81.5],
        historico_volumes=[1000, 1100, 1200, 1300],
    )
    assert resultado["tendencia_volume"] == "aumentando"


def test_analise_progresso_reducao():
    """Volume reduzindo gera recomendação de ajuste."""
    resultado = analisar_progresso(
        historico_pesos=[80, 79, 78],
        historico_volumes=[1200, 1000, 800],
    )
    assert resultado["ajuste_sugerido_pct"] > 0
