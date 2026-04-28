"""IA Modo B — Ollama local (LLM local via ollama)."""

from typing import Any, Dict
import httpx
from app.core.config import settings
from app.services.ai.base import BaseAIService
from app.services.ai.offline import OfflineAIService


class OllamaAIService(BaseAIService):
    """Usa LLM local via Ollama. Fallback para Modo A se indisponível."""

    def __init__(self):
        self.offline = OfflineAIService()
        self.endpoint = settings.OLLAMA_ENDPOINT
        self.model = settings.OLLAMA_MODEL

    async def _query(self, prompt: str) -> str:
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.endpoint}/api/generate",
                    json={"model": self.model, "prompt": prompt, "stream": False},
                )
                return response.json().get("response", "")
        except Exception:
            return ""

    async def generate_workout_plan(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Usa offline como base e enriquece com LLM se disponível
        result = await self.offline.generate_workout_plan(params)
        result["ia_mode"] = "B"
        return result

    async def generate_nutrition_plan(self, params: Dict[str, Any]) -> Dict[str, Any]:
        result = await self.offline.generate_nutrition_plan(params)
        result["ia_mode"] = "B"
        return result

    async def analyze_progress(self, params: Dict[str, Any]) -> Dict[str, Any]:
        result = await self.offline.analyze_progress(params)
        result["ia_mode"] = "B"
        return result
