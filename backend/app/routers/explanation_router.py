# backend/app/routers/explanation_router.py
from fastapi import APIRouter
from fastapi.responses import FileResponse
from pathlib import Path
from app.services.explanation_templates import ExplanationTemplates

router = APIRouter(prefix="/api/v1/explanations", tags=["explanations"])
templates = ExplanationTemplates()

@router.get("/template/{issue_code}")
async def get_template(
    issue_code: str,
    level: str = "intermediate"
):
    print(f"Fetching template for issue_code: {issue_code}, level: {level}")
    template = templates.get_template(issue_code, level)
    if not template:
        return {"detail": "Template not found dude"}
    return template

@router.get("/template-file")
async def get_raw_template_file():
    """For admin purposes - download the template JSON"""
    path = Path(__file__).parent.parent / "services" / "explanation_templates.json"
    return FileResponse(path)