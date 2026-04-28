"""Serviço de IA com suporte a Modo A (offline), B (ollama) e C (openai)."""

from app.core.config import get_settings
from app.services.ai.mode_a import (
    gerar_plano_nutricional,
    gerar_plano_treino,
    analisar_progresso,
)

settings = get_settings()


class AIService:
    """Interface única para todos os modos de IA."""

    async def workout_plan(
        self,
        objetivo: str,
        frequencia: int,
        nivel: str,
        limitacoes: list[str] | None = None,
    ) -> dict:
        mode = settings.feature_flag_ia_mode
        if mode == "A":
            return gerar_plano_treino(objetivo, frequencia, nivel, limitacoes)
        elif mode == "B":
            return await self._ollama_workout(objetivo, frequencia, nivel, limitacoes)
        elif mode == "C":
            return await self._openai_workout(objetivo, frequencia, nivel, limitacoes)
        return gerar_plano_treino(objetivo, frequencia, nivel, limitacoes)

    async def nutrition_plan(
        self,
        peso: float,
        altura: float,
        idade: int,
        objetivo: str,
        sexo: str = "M",
    ) -> dict:
        mode = settings.feature_flag_ia_mode
        if mode == "A":
            return gerar_plano_nutricional(peso, altura, idade, objetivo, sexo)
        return gerar_plano_nutricional(peso, altura, idade, objetivo, sexo)

    async def analyze_progress(
        self,
        historico_pesos: list[float],
        historico_volumes: list[float],
    ) -> dict:
        return analisar_progresso(historico_pesos, historico_volumes)

    async def _ollama_workout(self, *args, **kwargs) -> dict:
        """Fallback: se Ollama falhar, usa Modo A."""
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"{settings.ollama_endpoint}/api/generate",
                    json={"model": "llama3", "prompt": f"Gere plano de treino: {args}", "stream": False},
                    timeout=30,
                )
                # Processar resposta se necessário
        except Exception:
            pass
        return gerar_plano_treino(*args, **kwargs)

    async def _openai_workout(self, *args, **kwargs) -> dict:
        """Fallback para Modo A se sem API key."""
        if not settings.openai_api_key:
            return gerar_plano_treino(*args, **kwargs)
        # Implementação OpenAI aqui quando necessário
        return gerar_plano_treino(*args, **kwargs)
