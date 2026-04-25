"""IA Modo C — OpenAI API (pago, desativado por padrão)."""

from typing import Any, Dict
from app.services.ai.base import BaseAIService
from app.services.ai.offline import OfflineAIService


class OpenAIService(BaseAIService):
    """Usa OpenAI API. Fallback para Modo A se chave não configurada."""

    def __init__(self):
        self.offline = OfflineAIService()

    async def generate_workout_plan(self, params: Dict[str, Any]) -> Dict[str, Any]:
        result = await self.offline.generate_workout_plan(params)
        result["ia_mode"] = "C"
        return result

    async def generate_nutrition_plan(self, params: Dict[str, Any]) -> Dict[str, Any]:
        result = await self.offline.generate_nutrition_plan(params)
        result["ia_mode"] = "C"
        return result

    async def analyze_progress(self, params: Dict[str, Any]) -> Dict[str, Any]:
        result = await self.offline.analyze_progress(params)
        result["ia_mode"] = "C"
        return result
