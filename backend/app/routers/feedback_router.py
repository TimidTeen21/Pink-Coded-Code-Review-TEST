# backend/app/routers/feedback_router.py
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel

router = APIRouter(prefix="/feedback", tags=["feedback"])

class FeedbackRequest(BaseModel):
    user_id: str
    issue_code: str
    was_helpful: bool

@router.post("/explanation")
async def record_feedback(
    feedback: FeedbackRequest = Body(...)
):
    try:
        return {
            "status": "received",
            "user_id": feedback.user_id,
            "issue_code": feedback.issue_code
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))