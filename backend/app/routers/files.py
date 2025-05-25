# filepath: c:\Users\Admin\Pink Coded\Pink-Coded-Code-Review\backend\app\routers\files.py
from fastapi import APIRouter, HTTPException, Query
from pathlib import Path
import logging
from pydantic import BaseModel
from typing import Optional, List
from app.routers.analysis import router as analysis_router

# Get session tracking from analysis router
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
    path: str = Query(...),
    session_id: str = Query(...),
    temp_dir: Optional[str] = Query(None)
):
    try:
        clean_path = Path(path.strip('/'))
        
        # Debug: Log all available files
        if session_id in ACTIVE_SESSIONS:
            session_path = Path(ACTIVE_SESSIONS[session_id])
            logger.info(f"Available files in session:")
            for f in session_path.rglob('*'):
                logger.info(f"- {f.relative_to(session_path)}")

        # First try the exact path
        potential_paths = [clean_path]
        
        # Then try common variations
        potential_paths.extend([
            Path("upload") / clean_path,
            clean_path.with_name(clean_path.name),  # Just the filename
            Path("upload") / clean_path.name
        ])
        
        for file_path in potential_paths:
            full_path = Path(temp_dir or ACTIVE_SESSIONS[session_id]) / file_path
            if full_path.exists() and full_path.is_file():
                return {
                    "content": full_path.read_text(encoding='utf-8'),
                    "path": str(file_path)
                }
                
        raise HTTPException(404, detail=f"File not found at any of: {potential_paths}")
        
    except Exception as e:
        logger.error(f"File error: {str(e)}")
        raise HTTPException(500, detail=str(e))
    
@router.get("/debug")
async def debug_files(session_id: str):
    if session_id not in ACTIVE_SESSIONS:
        raise HTTPException(404, detail="Session not found")
    
    session_path = Path(ACTIVE_SESSIONS[session_id])
    files = []
    
    for path in session_path.rglob('*'):
        if path.is_file():
            files.append({
                "path": str(path.relative_to(session_path)),
                "size": path.stat().st_size,
                "modified": path.stat().st_mtime
            })
    
    return {
        "session_path": str(session_path),
        "files": files
    }