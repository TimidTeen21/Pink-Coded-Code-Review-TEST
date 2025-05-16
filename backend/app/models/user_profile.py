# filepath: c:\Users\Admin\Pink Coded\Pink-Coded-Code-Review\backend\app\models\user_profile.py
from pydantic import BaseModel, EmailStr
from typing import Optional
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

class UserInDB(UserBase):
    id: str
    hashed_password: str
    experience_level: ExperienceLevel = ExperienceLevel.INTERMEDIATE
    quiz_completed: bool = False
    quiz_score: Optional[int] = None
    preferences: dict = {}

class UserPublic(UserBase):
    id: str
    experience_level: ExperienceLevel
    quiz_completed: bool