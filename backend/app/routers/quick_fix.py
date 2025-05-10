from fastapi import APIRouter
from app.services.explanation_engine import ExplanationEngine

router = APIRouter(prefix="/api/v1/quick-fix", tags=["quick-fix"])

@router.post("/")
async def get_quick_fix(
    code: str,
    issue: str,
    engine: ExplanationEngine = Depends(ExplanationEngine)
):
    from app.models import Issue  # Mock issue
    mock_issue = Issue(
        code=issue,
        message="", 
        file="",
        line=0,
        severity="medium"
    )
    return {
        "fix": engine.generate_contextual_fix(mock_issue, code)
    }