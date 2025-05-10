# backend/app/routers/explanation_router.py
from fastapi import APIRouter, Query, HTTPException, Depends
from app.models import Issue
from app.dependencies import get_explanation_engine

router = APIRouter(
    prefix="/api/v1/explanations",
    tags=["explanations"],
    redirect_slashes=False
)

@router.get("", response_model=dict)
async def get_explanation(
    issue_code: str = Query(..., min_length=1),
    message: str = Query(..., min_length=1),
    file: str = Query(""),
    line: int = Query(0, ge=0),
    user_id: str = Query(..., min_length=1),
    engine=Depends(get_explanation_engine)
):
    try:
        issue = Issue(
            code=issue_code,
            message=message,
            file=file,
            line=line,
            severity="medium"
        )
        return await engine.generate_explanation(issue, user_id)
    except Exception as e:
        raise HTTPException(500, detail=str(e))