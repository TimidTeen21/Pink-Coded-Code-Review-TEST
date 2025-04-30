# backend/app/services/profile_service.py
from pathlib import Path
import json
from app.models import UserProfile
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from .explanation_engine import ExplanationEngine


class ProfileService:
    def __init__(self, storage_path: str = "user_profiles"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
    
    def get_profile(self, user_id: str) -> UserProfile:
        profile_path = self.storage_path / f"{user_id}.json"
        if profile_path.exists():
            return UserProfile(**json.loads(profile_path.read_text()))
        return UserProfile(user_id=user_id)
    
    def save_profile(self, profile: UserProfile):
        profile_path = self.storage_path / f"{profile.user_id}.json"
        profile_path.write_text(profile.json(indent=2))

def update_level_based_on_feedback(
    self, 
    user_id: str,
    was_helpful: bool,
    issue_complexity: str
):
    profile = self.get_profile(user_id)
    
    if was_helpful and issue_complexity == profile.experience_level:
        # User understood this level - consider moving up
        if profile.experience_level == "beginner":
            profile.experience_level = "intermediate"
        elif profile.experience_level == "intermediate":
            profile.experience_level = "advanced"
    
    elif not was_helpful:
        # Explanation was confusing - consider moving down
        if profile.experience_level == "advanced":
            profile.experience_level = "intermediate"
        elif profile.experience_level == "intermediate":
            profile.experience_level = "beginner"
    
    self.save_profile(profile)