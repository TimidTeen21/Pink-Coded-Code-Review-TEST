# backend/app/routers/feedback_router.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
import logging

# Configure logger
logger = logging.getLogger("feedback_logger")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

router = APIRouter(prefix="/feedback", tags=["feedback"])

class FeedbackRequest(BaseModel):
    user_id: str
    issue_code: str
    was_helpful: bool
    explanation_level: str  # "beginner"/"intermediate"/"advanced"

@router.post("/explanation")
async def log_feedback(feedback: FeedbackRequest):
    try:
        # Log the feedback (replace with your actual storage logic)
        logger.info(f"Feedback received: {feedback.dict()}")
        
        # In a real implementation, you would:
        # 1. Get the user profile
        # 2. Update their feedback log
        # 3. Save the profile
        
        return {"status": "success", "message": "Feedback recorded"}
        
    except Exception as e:
        logger.error(f"Feedback error: {str(e)}")
        raise HTTPException(500, detail=str(e))