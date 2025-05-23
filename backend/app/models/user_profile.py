# backend/app/models/user_profile.py
from pydantic import BaseModel, EmailStr, Field
from typing import Dict, Set, Optional, List
from enum import Enum

class ExperienceLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class UserBase(BaseModel):
    email: EmailStr
    username: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    experience_level: Optional[ExperienceLevel] = None
    preferences: Optional[Dict[str, str]] = None

class UserInDB(UserBase):
    id: str
    hashed_password: str
    experience_level: ExperienceLevel = ExperienceLevel.INTERMEDIATE
    quiz_completed: bool = False
    quiz_score: Optional[int] = None
    preferences: Dict[str, str] = Field(default_factory=dict)
    known_concepts: Set[str] = Field(default_factory=set)
    weak_areas: Set[str] = Field(default_factory=set)
    seen_issues: Dict[str, int] = Field(default_factory=dict)  # Format: {"E501": 3, "B101": 1}
    favorite_fixes: Dict[str, List[str]] = Field(default_factory=dict)  # Format: {"E501": ["fix1", "fix2"]}

class UserPublic(UserBase):
    id: str
    experience_level: ExperienceLevel
    quiz_completed: bool
    known_concepts: Set[str]
    weak_areas: Set[str]

class UserProfile(BaseModel):
    """
    Comprehensive user profile for code analysis personalization.
    Used by the explanation engine to tailor feedback.
    """
    user_id: str
    experience_level: ExperienceLevel = ExperienceLevel.INTERMEDIATE
    known_concepts: Set[str] = Field(
        default_factory=set,
        description="Programming concepts the user is familiar with (e.g., OOP, decorators)"
    )
    weak_areas: Set[str] = Field(
        default_factory=set,
        description="Concepts the user struggles with"
    )
    seen_issues: Dict[str, int] = Field(
        default_factory=dict,
        description="Frequency of encountered issues (issue_code: count)"
    )
    preferred_explanation_depth: str = Field(
        default="balanced",
        description="'simple', 'balanced', or 'technical'"
    )
    learning_style: str = Field(
        default="examples",
        description="'examples', 'analogies', or 'technical'"
    )
    flamingo_points: int = Field(
        default=0,
        description="Gamification points earned"
    )
    achievements: Set[str] = Field(
        default_factory=set,
        description="Earned achievement badges"
    )

    def update_from_quiz(self, score: int, level: ExperienceLevel):
        """Update profile based on quiz results"""
        self.experience_level = level
        self.flamingo_points += score * 10
        self.quiz_completed = True
        
        if score > 80:
            self.achievements.add("quick_learner")
        if level == ExperienceLevel.ADVANCED:
            self.achievements.add("code_master")

    def record_issue(self, issue_code: str):
        """Track how often user sees specific issues"""
        self.seen_issues[issue_code] = self.seen_issues.get(issue_code, 0) + 1
        
        # Auto-detect weak areas
        if self.seen_issues[issue_code] > 3:
            self.weak_areas.add(issue_code.split()[0])  # Add base error code

    def adjust_level_based_on_feedback(self, was_helpful: bool):
        """Adjust expertise level based on explanation feedback"""
        if was_helpful:
            if self.experience_level == ExperienceLevel.BEGINNER:
                self.flamingo_points += 5
            elif self.experience_level == ExperienceLevel.INTERMEDIATE:
                self.flamingo_points += 3
        else:
            if self.experience_level == ExperienceLevel.ADVANCED:
                self.experience_level = ExperienceLevel.INTERMEDIATE
            elif self.experience_level == ExperienceLevel.INTERMEDIATE:
                self.flamingo_points -= 2