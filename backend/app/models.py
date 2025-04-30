# backend/app/models.py
from pydantic import BaseModel
from typing import Dict, Set, Literal, Optional

ExperienceLevel = Literal["beginner", "intermediate", "advanced"]

class Issue(BaseModel):
    """Standardized issue representation"""
    code: str
    message: str
    file: str
    line: int
    severity: str = "warning"
    linter: str = "unknown"

class UserProfile(BaseModel):
    user_id: str
    experience_level: ExperienceLevel = "intermediate"
    known_concepts: Set[str] = set()
    weak_areas: Set[str] = set()
    seen_issues: Dict[str, int] = {}