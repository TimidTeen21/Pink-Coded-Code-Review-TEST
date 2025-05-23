# backend/app/routers/analysis.py
from fastapi import APIRouter, HTTPException, UploadFile, File, Body, Depends
import subprocess
import uuid
from typing import Dict, Any, List, Optional
from pathlib import Path
import json
from pydantic import BaseModel
import logging
import configparser
import toml
import shutil
import tempfile
import zipfile
from enum import Enum
import atexit
from fastapi.responses import FileResponse
from app.models.user_profile import UserInDB
from app.routers.auth import get_current_user


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global state for session management
ACTIVE_SESSIONS: Dict[str, str] = {}  # session_id -> temp_dir
ACTIVE_ANALYSES: Dict[str, dict] = {}  # session_id -> analysis results
ANALYSIS_TEMP_DIRS: Dict[str, Path] = {}  # Track analysis directories by session/user

router = APIRouter(prefix="/api/v1/analysis", tags=["analysis"])

# Expose session tracking variables to other modules
router.ACTIVE_SESSIONS = ACTIVE_SESSIONS
router.ACTIVE_ANALYSES = ACTIVE_ANALYSES
router.ANALYSIS_TEMP_DIRS = ANALYSIS_TEMP_DIRS

class AnalysisRequest(BaseModel):
    project_path: str
    project_type: Optional[str] = None
    linter: Optional[str] = None

class ProjectType(str, Enum):
    WEB = "web"
    EMBEDDED = "embedded"
    SECURITY = "security"
    UNKNOWN = "unknown"

class Linter(str, Enum):
    RUFF = "ruff"
    PYLINT = "pylint"
    BANDIT = "bandit"
    RADON = "radon"

class LinterConfig:
    @staticmethod
    def get_ruff_config() -> Dict[str, Any]:
        return {
            "lint": {
                "select": ["E", "F", "W", "B", "I", "UP", "D"],
                "ignore": ["E501", "D203", "D212"],
                "per-file-ignores": {
                    "__init__.py": ["F401"],
                    "tests/*": ["S101"]
                }
            }
        }

    @staticmethod
    def get_pylint_config() -> Dict[str, Any]:
        return {
            "MASTER": {
                "load-plugins": "pylint.extensions.mccabe"
            },
            "MESSAGES CONTROL": {
                "disable": "missing-docstring,too-few-public-methods,invalid-name"
            }
        }

    @staticmethod
    def get_bandit_config() -> Dict[str, Any]:
        return {
            'target': ['*'],
            'recursive': True,
            'confidence': 'low',
            'severity': 'low',
            'tests': [],
            'skips': []
        }

def setup_linter_config(linter: str) -> Path:
    """Create temporary linter configuration file"""
    config_dir = Path("/tmp/pink-coded-config")
    config_dir.mkdir(exist_ok=True)
    
    if linter == Linter.RUFF:
        config_path = config_dir / "ruff.toml"
        with open(config_path, "w") as f:
            toml.dump(LinterConfig.get_ruff_config(), f)
    elif linter == Linter.PYLINT:
        config_path = config_dir / ".pylintrc"
        parser = configparser.ConfigParser()
        parser.read_dict(LinterConfig.get_pylint_config())
        parser.write(config_path.open("w"))
    elif linter == Linter.BANDIT:
        config_path = config_dir / ".bandit"
        with open(config_path, "w") as f:
            json.dump(LinterConfig.get_bandit_config(), f)
    else:
        config_path = config_dir / "config.ini"
    
    return config_path

def detect_project_type(project_path: Path) -> str:
    """Detect project type based on file patterns"""
    markers = {
        ProjectType.WEB: {"requirements.txt", "pyproject.toml", "django", "flask"},
        ProjectType.EMBEDDED: {"platformio.ini", "Makefile", ".ino", ".c"},
        ProjectType.SECURITY: {"auth", "crypto", "security", "jwt"}
    }
    
    scores = {pt: 0 for pt in ProjectType}
    for item in project_path.rglob("*"):
        if item.is_file():
            for pt, patterns in markers.items():
                if any(p in item.name.lower() or p in str(item.relative_to(project_path)).lower() 
                      for p in patterns):
                    scores[pt] += 1
    
    if max(scores.values()) == 0:
        return ProjectType.UNKNOWN
    return max(scores.items(), key=lambda x: x[1])[0]

def generate_flamingo_message(issue: dict) -> str:
    """
    Generate a user-friendly message for a linter issue.
    """
    return f"[{issue.get('type', '').capitalize()}] {issue.get('code', '')}: {issue.get('message', '')}"

def parse_linter_output(output: str, linter: str, base_path: Path) -> List[Dict[str, Any]]:
    """Parse linter output into standardized format"""
    if not output.strip():
        return []
    
    try:
        if linter == Linter.RUFF:
            issues = json.loads(output)
            parsed = []
            for issue in issues:
                file_path = Path(issue["filename"])
                rel_path = str(file_path.relative_to(base_path)) if file_path.is_absolute() else issue["filename"]
                issue_type = "warning"  # Default to warning for Ruff
                
                # Map specific codes to error level
                if issue["code"].startswith(("E", "F")):
                    issue_type = "error"
                
                parsed.append({
                    "type": issue_type,
                    "file": rel_path,
                    "line": issue["location"]["row"],
                    "message": issue["message"],
                    "code": issue["code"],
                    "url": issue.get("url", ""),
                    "flamingo_message": generate_flamingo_message({
                        "code": issue["code"],
                        "message": issue["message"],
                        "type": issue_type
                    })
                })
            return parsed

        elif linter == Linter.PYLINT:
            issues = json.loads(output)
            parsed = []
            for issue in issues:
                file_path = Path(issue["path"])
                rel_path = str(file_path.relative_to(base_path)) if file_path.is_absolute() else issue["path"]
                parsed.append({
                    "type": issue["type"].lower(),
                    "file": rel_path,
                    "line": issue["line"],
                    "message": issue["message"],
                    "code": issue["message-id"],
                    "url": ""
                })
            return parsed

        elif linter == Linter.BANDIT:
            try:
                data = json.loads(output)
                if not isinstance(data, dict) or "results" not in data:
                    logger.error(f"Invalid Bandit output structure: {output[:200]}...")
                    return []
                
                parsed = []
                for issue in data["results"]:
                    file_path = Path(issue["filename"])
                    rel_path = str(file_path.relative_to(base_path)) if file_path.is_absolute() else issue["filename"]
                    
                    parsed.append({
                        "type": "security",
                        "file": rel_path,
                        "line": issue["line_number"],
                        "message": issue["issue_text"],
                        "code": issue["test_id"],
                        "url": issue["more_info"],
                        "severity": issue["issue_severity"].lower(),
                        "confidence": issue["issue_confidence"].lower()
                    })
                return parsed
            except Exception as e:
                logger.error(f"Bandit parse error: {str(e)}")
                return []

    except Exception as e:
        logger.error(f"Error parsing {linter} output: {e}")
        return []

def parse_radon_output(output: str, base_path: Path) -> List[Dict[str, Any]]:
    """Parse Radon complexity analysis output"""
    try:
        try:
            data = json.loads(output)
            if isinstance(data, str):
                data = json.loads(data)
        except json.JSONDecodeError:
            logger.error(f"Invalid Radon output: {output[:200]}...")
            return []

        issues = []
        for file_path, items in data.items():
            rel_path = str(Path(file_path).relative_to(base_path)) if Path(file_path).is_absolute() else file_path
            
            for item in items:
                if not isinstance(item, dict):
                    continue
                    
                complexity = item.get("complexity", 0)
                if complexity <= 1:
                    continue
                
                issues.append({
                    "type": "complexity",
                    "file": rel_path,
                    "line": item.get("lineno", 0),
                    "message": f"{item.get('type', 'item').title()} '{item.get('name', '')}' (complexity: {complexity})",
                    "code": f"RADON-{item.get('rank', 'U')}",
                    "complexity": complexity,
                    "severity": "high" if complexity > 10 else "medium"
                })
                
        return issues
        
    except Exception as e:
        logger.error(f"Radon parse failed: {str(e)}")
        return []

async def run_single_linter(linter: str, project_path: Path) -> Dict[str, Any]:
    """Run an individual linter and return results"""
    try:
        logger.info(f"Running {linter} analysis in: {project_path}")
        
        # Check for Python files (except for Radon which analyzes complexity)
        if linter != Linter.RADON:
            py_files = list(project_path.rglob("*.py"))
            logger.info(f"Python files found: {len(py_files)}")
            if not py_files:
                return {
                    "success": True,
                    "output": "No Python files found",
                    "issues": [],
                    "raw_stderr": ""
                }

        config_path = setup_linter_config(linter)
        
        if linter == Linter.RUFF:
            cmd = [
                "ruff",
                "check",
                "--config", str(config_path),
                "--output-format=json",
                "--no-cache",
                str(project_path)
            ]
        elif linter == Linter.PYLINT:
            cmd = [
                "pylint",
                f"--rcfile={config_path}",
                "--output-format=json",
                "--recursive=y",
                str(project_path)
            ]
        elif linter == Linter.BANDIT:
            cmd = [
                "bandit",
                "-r",
                "-f", "json",
                "-c", str(config_path),
                str(project_path)
            ]
        elif linter == Linter.RADON:
            cmd = [
                "radon",
                "cc",
                "-j",
                str(project_path)
            ]
        else:
            raise ValueError(f"Unsupported linter: {linter}")

        logger.info(f"Executing: {' '.join(cmd)}")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(project_path),
            timeout=300
        )

        # Log output for debugging
        logger.info(f"{linter} stdout (first 500 chars):\n{result.stdout[:500]}...")
        if result.stderr:
            logger.info(f"{linter} stderr:\n{result.stderr}")

        # Handle success codes
        success = True
        if linter == Linter.RUFF:
            success = result.returncode in [0, 4]  # 0=no issues, 4=issues found
        elif linter == Linter.BANDIT:
            success = result.returncode in [0, 1]  # 0=no issues, 1=issues found
        else:
            success = result.returncode == 0

        # Parse output
        issues = []
        if linter == Linter.RADON:
            try:
                radon_data = json.loads(result.stdout)
                if isinstance(radon_data, str):  # Handle unexpected string output
                    radon_data = json.loads(radon_data)
                issues = parse_radon_output(json.dumps(radon_data), project_path)
            except Exception as e:
                logger.error(f"Radon parse failed: {e}")
                issues = []
        else:
            issues = parse_linter_output(result.stdout, linter, project_path)
        
        logger.info(f"{linter} analysis completed. Found {len(issues)} issues.")
        return {
            "success": success,
            "output": result.stdout,
            "issues": issues,
            "raw_stderr": result.stderr
        }

    except subprocess.TimeoutExpired:
        logger.error(f"{linter} analysis timed out")
        return {
            "success": False,
            "error": f"{linter} analysis timed out",
            "raw_stderr": "Process exceeded 5 minute limit"
        }
    except Exception as e:
        logger.error(f"{linter} failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "raw_stderr": str(e)
        }

async def run_linter_analysis(project_path: Path, experience_level: str) -> Dict[str, Any]:
    """Run all appropriate linters for the project"""
    # Always run security scanner first
    bandit_result = await run_single_linter(Linter.BANDIT, project_path)
    
    # Determine project type
    project_type = detect_project_type(project_path)
    
    # Run main linter based on type
    if project_type == ProjectType.WEB:
        main_result = await run_single_linter(Linter.RUFF, project_path)
    else:
        main_result = await run_single_linter(Linter.PYLINT, project_path)
    
    if experience_level == "beginner":
        # Filter out some complex issues for beginners
        main_result["issues"] = [issue for issue in main_result.get("issues", []) 
                               if not issue.get("code", "").startswith(("E", "F"))]

    # Always run complexity analysis
    radon_result = await run_single_linter(Linter.RADON, project_path)
    
    result = {
        "project_type": project_type.value if isinstance(project_type, Enum) else project_type,
        "linter": "ruff" if project_type == ProjectType.WEB else "pylint",
        "complexity": "radon",
        "security_scan": {
            "success": bandit_result["success"],
            "issues": bandit_result.get("issues", []),
            "error": bandit_result.get("error")
        },
        "main_analysis": {
            "success": main_result["success"],
            "issues": main_result.get("issues", []),
            "error": main_result.get("error")
        },
        "complexity_analysis": {
            "success": radon_result["success"],
            "issues": radon_result.get("issues", []),
            "error": radon_result.get("error")
        }
    }

    logger.info(f"Final analysis result structure: {json.dumps(result, indent=2)}")
    return {
        "project_type": project_type.value,
        "experience_level": experience_level,
        "result": result
    }

async def cleanup_temp_dirs():
    for session_id, temp_dir in ACTIVE_SESSIONS.items():
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception as e:
            logger.error(f"Error cleaning up {temp_dir}: {e}")
    ACTIVE_SESSIONS.clear()
    ACTIVE_ANALYSES.clear()
    ANALYSIS_TEMP_DIRS.clear()

atexit.register(cleanup_temp_dirs)

@router.post("/analyze-zip")
async def analyze_zip(
    zip_file: UploadFile = File(...),
    current_user: UserInDB = Depends(get_current_user)
):
    """Analyze a ZIP file containing a Python project"""
    session_id = str(uuid.uuid4())
    temp_dir = tempfile.mkdtemp(prefix=f"pink-coded-{session_id}-")
    ACTIVE_SESSIONS[session_id] = temp_dir
    
    try:
        zip_path = Path(temp_dir) / "upload.zip"
        with zip_path.open("wb") as buffer:
            shutil.copyfileobj(zip_file.file, buffer)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        result = await run_linter_analysis(Path(temp_dir), current_user.experience_level)
        ACTIVE_ANALYSES[session_id] = result  # Store full analysis results
        
        return {
            **result,
            "session_id": session_id,
            "temp_dir": temp_dir
        }
        
    except Exception as e:
        logger.error(f"ZIP analysis failed: {e}")
        raise HTTPException(500, detail=str(e))
        
@router.post("/generate-fix")
async def generate_fix(
    code: str = Body(...),
    issue: dict = Body(...),
    user_id: str = Body(...)
):
    """Generate a fix for a specific code issue"""
    try:
        # TODO: Replace with actual DeepSeek API call
        prompt = f"""Generate a fix for this Python issue:
        - File: {issue.get('file')}
        - Line: {issue.get('line')}
        - Error: {issue.get('code')} - {issue.get('message')}
        - Code Context:
        ```python
        {code}
        ```
        
        Provide ONLY the corrected code with minimal changes.
        Include brief explanation if the fix is non-trivial."""
        
        # Mock response - replace with actual API call
        if issue.get('code') == 'D100':
            return {
                "fix": '"""Module docstring"""\n' + code,
                "explanation": "Added missing module docstring"
            }
        else:
            return {
                "fix": code,  # Default to no changes
                "explanation": "No automatic fix available for this issue type"
            }
            
    except Exception as e:
        logger.error(f"Fix generation failed: {e}")
        raise HTTPException(500, detail=str(e))

@router.post("/analyze-code")
async def analyze_code(
    code: str = Body(...),
    file_path: str = Body(...),
    user_id: str = Body(...),
    session_id: str = Body(...),
    temp_dir: str = Body(None)
):
    try:
        # Basic validation
        if not code.strip():
            return {
                "main_analysis": {"issues": []},
                "complexity_analysis": {"issues": []},
                "security_scan": {"issues": []}
            }

        # Save to the original location
        if temp_dir:
            file_location = Path(temp_dir) / file_path
        elif session_id in ACTIVE_SESSIONS:
            file_location = Path(ACTIVE_SESSIONS[session_id]) / file_path
        else:
            file_location = Path(tempfile.mkdtemp()) / "temp_analysis.py"
        
        file_location.write_text(code)
        
        # Get the full analysis results from session
        if session_id in ACTIVE_ANALYSES:
            result = ACTIVE_ANALYSES[session_id]
            
            # Update just this file's issues in the results
            file_result = await run_single_linter(Linter.RUFF, file_location.parent)
            file_issues = file_result.get("issues", [])
            
            # Update the main analysis issues
            if result.get("main_analysis"):
                # Remove old issues for this file
                result["main_analysis"]["issues"] = [
                    issue for issue in result["main_analysis"]["issues"] 
                    if issue["file"] != file_path
                ]
                # Add new issues
                result["main_analysis"]["issues"].extend(file_issues)
            
            return result
        
        # If no session, just return current file analysis
        file_result = await run_single_linter(Linter.RUFF, file_location.parent)
        return {
            "main_analysis": {
                "success": True,
                "issues": file_result.get("issues", [])
            },
            "complexity_analysis": {"issues": []},
            "security_scan": {"issues": []}
        }
        
    except json.JSONDecodeError:
        logger.error("Invalid JSON in analysis request")
        raise HTTPException(400, detail="Invalid code format")
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        raise HTTPException(500, detail="Analysis failed")
    
@router.post("/apply-fix")
async def apply_fix(
    file_path: str = Body(...),
    issue: dict = Body(...),
    fix: str = Body(...),
    session_id: str = Body(...),
    temp_dir: str = Body(None)
):
    """Apply a fix to a specific file"""
    try:
        # Locate the file
        file_location = None
        if temp_dir:
            file_location = Path(temp_dir) / file_path
        elif session_id in ACTIVE_SESSIONS:
            file_location = Path(ACTIVE_SESSIONS[session_id]) / file_path
        
        if not file_location or not file_location.exists():
            raise HTTPException(404, detail="File not found")
        
        # Apply the fix
        content = file_location.read_text()
        lines = content.splitlines()
        
        # Simple line replacement
        if issue.get('line'):
            line_num = issue['line'] - 1
            if 0 <= line_num < len(lines):
                lines[line_num] = fix
        
        new_content = '\n'.join(lines)
        file_location.write_text(new_content)
        
        return {
            "success": True,
            "new_content": new_content,
            "message": "Fix applied successfully",
            "file_path": str(file_location)
        }
    except Exception as e:
        logger.error(f"Fix failed: {e}")
        raise HTTPException(500, detail=str(e))
    
@router.post("/export-project")
async def export_project(
    session_id: str = Body(...),
    temp_dir: str = Body(None)
):
    """Export the analyzed project as a ZIP file"""
    try:
        working_dir = None
        if temp_dir:
            working_dir = Path(temp_dir)
        elif session_id in ACTIVE_SESSIONS:
            working_dir = Path(ACTIVE_SESSIONS[session_id])
        
        if not working_dir or not working_dir.exists():
            raise HTTPException(404, detail="Project not found")
        
        # Create a new ZIP
        zip_filename = f"pink-coded-export-{session_id[:8]}.zip"
        zip_path = working_dir.parent / zip_filename
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file in working_dir.rglob('*'):
                if file.is_file():
                    zipf.write(file, file.relative_to(working_dir))
        
        return FileResponse(
            path=zip_path,
            filename=zip_filename,
            media_type='application/zip'
        )
    except Exception as e:
        logger.error(f"Export failed: {e}")
        raise HTTPException(500, detail=str(e))

@router.get("/debug-config")
async def debug_config():
    """Debug endpoint to check active linter configs"""
    configs = {}
    for linter in [Linter.RUFF, Linter.PYLINT, Linter.BANDIT]:
        config_path = setup_linter_config(linter)
        if config_path.exists():
            configs[linter] = config_path.read_text()
    return configs