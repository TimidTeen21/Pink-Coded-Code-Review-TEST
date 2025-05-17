# backend/app/services/profile_service.py
from pathlib import Path
import json
from app.models import UserProfile
from typing import TYPE_CHECKING
from typing import Optional
from app.models import UserPublic, ExperienceLevel
from app.models.user_profile import UserInDB



if TYPE_CHECKING:
    from .explanation_engine import ExplanationEngine


class ProfileService:
    def __init__(self, storage_path: str = "user_profiles"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
    
    def get_profile(self, user_id: str) -> Optional[UserInDB]:
        profile_path = self.storage_path / f"{user_id}.json"
        if profile_path.exists():
            try:
                with open(profile_path, "r") as f:
                    data = json.load(f)
                    return UserInDB(**data)
            except:
                return None
        return None
    
    def save_profile(self, profile: UserInDB):
        profile_path = self.storage_path / f"{profile.id}.json"
        with open(profile_path, "w") as f:
            json.dump(profile.dict(), f)
    
    def update_experience_level(self, user_id: str, level: ExperienceLevel):
        profile = self.get_profile(user_id)
        if profile:
            profile.experience_level = level
            self.save_profile(profile)
    
    def complete_quiz(self, user_id: str, score: int):
        profile = self.get_profile(user_id)
        if profile:
            profile.quiz_completed = True
            profile.quiz_score = score
            self.save_profile(profile)