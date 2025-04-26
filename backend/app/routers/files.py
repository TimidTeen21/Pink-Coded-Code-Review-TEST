from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/files", tags=["files"])

class DirectoryResponse(BaseModel):
    status: str
    message: str = "Use browser's file picker instead"

@router.post("/select-directory")
async def select_directory():
    """Endpoint to inform frontend to use browser picker"""
    return DirectoryResponse(status="browser-picker-required")