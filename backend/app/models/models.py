# backend/app/models.py
from pydantic import BaseModel
from typing import Dict, Set, Literal

ExperienceLevel = Literal["beginner", "intermediate", "advanced"]

class UserProfile(BaseModel):
    user_id: str  # Can be auth token or session ID
    experience_level: ExperienceLevel = "intermediate"
    known_concepts: Set[str] = set()  # E.g., {"OOP", "recursion"}
    weak_areas: Set[str] = set()      # E.g., {"decorators", "context managers"}
    seen_issues: Dict[str, int] = {}  # Format: {"E501": 3, "B101": 1}