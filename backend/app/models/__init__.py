from app.core.database import Base
from .user import User, PersonalClient
from .photo import Photo
from .workout import Workout
from .nutrition import NutritionLog  # Garanta que o nome da classe no arquivo nutrition.py é esse
from .ai_recommendation import AIRecommendation # ESSA É A PEÇA QUE FALTA

__all__ = ["Base", "User", "PersonalClient", "Photo", "Workout", "NutritionLog", "AIRecommendation"]