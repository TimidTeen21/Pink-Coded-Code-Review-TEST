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
    path: str = Query(..., description="Relative path to the file"),
    session_id: str = Query(..., description="Current session ID"),
    temp_dir: Optional[str] = Query(None, description="Explicit temp directory path")
):
    try:
        # Normalize path (handle Windows/Unix paths)
        clean_path = Path(path.strip('/')).as_posix()
        filename = clean_path.split('/')[-1]
        
        # Try these locations in order:
        possible_locations = []
        
        # 1. Check explicit temp_dir if provided
        if temp_dir:
            temp_path = Path(temp_dir)
            possible_locations.extend([
                temp_path / clean_path,
                temp_path / filename,
                temp_path / "upload" / clean_path,
                temp_path / "upload" / filename
            ])
        
        # 2. Check session directory
        if session_id in ACTIVE_SESSIONS:
            session_path = Path(ACTIVE_SESSIONS[session_id])
            possible_locations.extend([
                session_path / clean_path,
                session_path / filename,
                session_path / "upload" / clean_path,
                session_path / "upload" / filename,
                session_path / "project" / clean_path,
                session_path / "project" / filename
            ])
        
        # Try each possible location
        found_path = None
        for location in possible_locations:
            if location.exists() and location.is_file():
                found_path = location
                break
        
        if not found_path:
            searched = "\n".join([str(p) for p in possible_locations])
            logger.error(f"File not found. Searched locations:\n{searched}")
            raise HTTPException(
                status_code=404,
                detail={
                    "message": f"File '{clean_path}' not found",
                    "searched_locations": [str(p) for p in possible_locations]
                }
            )
        
        return {
            "content": found_path.read_text(encoding='utf-8'),
            "path": str(found_path.relative_to(Path(ACTIVE_SESSIONS[session_id]))) 
                    if session_id in ACTIVE_SESSIONS 
                    else str(found_path)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File read error: {str(e)}")
        raise HTTPException(500, detail=str(e))