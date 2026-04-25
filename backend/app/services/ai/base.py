"""Interface base para serviços de IA."""

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseAIService(ABC):
    """Contrato que todos os modos de IA devem implementar."""

    @abstractmethod
    async def generate_workout_plan(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Gera plano de treino semanal."""
        ...

    @abstractmethod
    async def generate_nutrition_plan(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Gera plano nutricional."""
        ...

    @abstractmethod
    async def analyze_progress(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa progresso e gera recomendações."""
        ...


def get_ai_service() -> BaseAIService:
    """Factory que retorna o serviço de IA correto baseado na feature flag."""
    from app.core.config import settings

    mode = settings.FEATURE_FLAG_IA_MODE

    if mode == "A":
        from app.services.ai.offline import OfflineAIService
        return OfflineAIService()
    elif mode == "B":
        from app.services.ai.ollama import OllamaAIService
        return OllamaAIService()
    elif mode == "C":
        from app.services.ai.openai_service import OpenAIService
        return OpenAIService()
    else:
        from app.services.ai.offline import OfflineAIService
        return OfflineAIService()
