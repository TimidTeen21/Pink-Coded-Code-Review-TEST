# filepath: c:\Users\Admin\Pink Coded\Pink-Coded-Code-Review\backend\app\routers\files.py
from fastapi import APIRouter, HTTPException, Query
from pathlib import Path
import logging
from pydantic import BaseModel
from typing import Optional
from app.routers.analysis import router as analysis_router


ACTIVE_SESSIONS = analysis_router.ACTIVE_SESSIONS
ACTIVE_ANALYSES = analysis_router.ACTIVE_ANALYSES 
ANALYSIS_TEMP_DIRS = analysis_router.ANALYSIS_TEMP_DIRS

router = APIRouter(prefix="/api/v1/files", tags=["files"])

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class DirectoryResponse(BaseModel):
    status: str
    message: str = "Use browser's file picker instead"

@router.get("")
async def get_file_contents(
    path: str,
    session_id: Optional[str] = Query(...),
    temp_dir: str = Query(None)
):
    try:
        # Try exact path first
        if temp_dir:
            exact_path = Path(temp_dir) / path
            if exact_path.exists():
                return {"content": exact_path.read_text()}
        
        # Fallback to session-based lookup
        if session_id in ACTIVE_SESSIONS:
            session_path = Path(ACTIVE_SESSIONS[session_id]) / path
            if session_path.exists():
                return {"content": session_path.read_text()}
        
        raise HTTPException(404, detail=f"File not found at: {path}")
        
    except Exception as e:
        logger.error(f"Failed to read file {path}: {str(e)}")
        raise HTTPException(500, detail=str(e))


