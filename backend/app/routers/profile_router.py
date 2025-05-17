# filepath: c:\Users\Admin\Pink Coded\Pink-Coded-Code-Review\backend\app\routers\profile_router.py
from fastapi import APIRouter, Depends, HTTPException
from app.models.user_profile import ExperienceLevel
from app.services.profile_service import ProfileService
from app.routers.auth import get_current_user
from app.models.user_profile import UserInDB

router = APIRouter(prefix="/api/v1/profile", tags=["profile"])

@router.post("/quiz")
async def submit_quiz(
    score: int,
    level: ExperienceLevel,
    current_user: UserInDB = Depends(get_current_user)
):
    profile_service = ProfileService()
    profile_service.complete_quiz(current_user.id, score)
    profile_service.update_experience_level(current_user.id, level)
    return {"status": "success"}

@router.get("/experience-level")
async def get_experience_level(
    current_user: UserInDB = Depends(get_current_user)
):
    return {"level": current_user.experience_level}

@router.post("/experience-level")
async def update_experience_level(
    level: ExperienceLevel,
    current_user: UserInDB = Depends(get_current_user)
):
    profile_service = ProfileService()
    profile_service.update_experience_level(current_user.id, level)
    return {"status": "success"}