# backend/app/routers/feedback_router.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.profile_service import ProfileService

router = APIRouter(prefix="/api/v1/feedback", tags=["feedback"])
profile_service = ProfileService()

class FeedbackRequest(BaseModel):
    user_id: str
    issue_code: str
    was_helpful: bool
    explanation_level: str  # "beginner"/"intermediate"/"advanced"

@router.post("/explanation")
async def log_feedback(feedback: FeedbackRequest):
    try:
        profile = profile_service.get_profile(feedback.user_id)
        
        # Track feedback for reinforcement learning
        profile.feedback_log.append({
            "issue_code": feedback.issue_code,
            "helpful": feedback.was_helpful,
            "level": feedback.explanation_level,
            "timestamp": datetime.utcnow()
        })
        
        # Update user's preference weights
        if feedback.was_helpful:
            profile.preferred_complexity[feedback.explanation_level] += 1
        
        profile_service.save_profile(profile)
        return {"status": "feedback_recorded"}
    
    except Exception as e:
        raise HTTPException(500, f"Feedback logging failed: {str(e)}")