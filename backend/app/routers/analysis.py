# backend/app/routers/analysis.py
from fastapi import APIRouter, HTTPException, UploadFile, File, Body, Depends
import subprocess
import os
import asyncio
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
from app.services.parse_linter import parse_linter_output as parse_linter_output_service
from app.services.parse_linter import LinterType

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
            "select": [
                "E",   # Pyflakes errors
                "F",   # Pyflakes fixes
                "W",   # Pyflakes warnings
                "B9",  # Bugbear (updated from "B")
                "I",   # isort (import sorting)
                "UP",  # pyupgrade (modern Python)
                "D",   # pydocstyle (docstrings)
                "C4",  # Comprehensions
                "RUF", # Ruff-specific rules
            ],
            "ignore": ["E501"],  # Ignore line length (handled by formatters)
            "per-file-ignores": {
                "tests/*": ["S101"]  # Allow `assert` in tests
            },
            # "strict": True,  # Only enable if you want ALL rules
        },
       
    }

    @staticmethod 
    def get_pylint_config() -> Dict[str, Any]:
        return {
            "MASTER": {
                "load-plugins": "pylint.extensions.mccabe",
                "enable-all-extensions": True
            },
            "MESSAGES CONTROL": {
                "disable": ""
            },
            "BASIC": {
                "good-names": ["i", "j", "k", "ex", "run", "_"]
            }
        }

    @staticmethod
    def get_bandit_config() -> Dict[str, Any]:
        return {
            'target': ['*'],
            'recursive': True,
            'confidence': 'high',
            'severity': 'high',
            'tests': [],
            'skips': []
        }

import toml
import json
import configparser
from pathlib import Path
from typing import Union

def setup_linter_config(linter: str) -> Path:
    """Create temporary linter configuration file with validation."""
    config_dir = Path("/tmp/pink-coded-config")
    config_dir.mkdir(exist_ok=True)

    try:
        if linter == Linter.RUFF:
            config_path = config_dir / "ruff.toml"
            ruff_config = LinterConfig.get_ruff_config()
            
            # Validate the config is a valid TOML-serializable dict
            if not isinstance(ruff_config, dict):
                raise ValueError("Ruff config must be a dictionary")
            
            # Write and verify the file
            with open(config_path, "w") as f:
                toml.dump(ruff_config, f)
            
            # Verify the file can be read back
            with open(config_path, "r") as f:
                toml.load(f)  # Raises toml.TomlDecodeError if invalid
            
        elif linter == Linter.PYLINT:
            config_path = config_dir / ".pylintrc"
            parser = configparser.ConfigParser()
            pylint_config = LinterConfig.get_pylint_config()
            
            if not isinstance(pylint_config, dict):
                raise ValueError("Pylint config must be a nested dictionary")
                
            parser.read_dict(pylint_config)
            with open(config_path, "w") as f:
                parser.write(f)
                
        elif linter == Linter.BANDIT:
            config_path = config_dir / ".bandit"
            bandit_config = LinterConfig.get_bandit_config()
            
            if not isinstance(bandit_config, dict):
                raise ValueError("Bandit config must be a dictionary")
                
            with open(config_path, "w") as f:
                json.dump(bandit_config, f, indent=2)
                
        else:
            config_path = config_dir / "config.ini"
            
        return config_path
        
    except Exception as e:
        # Clean up invalid config files
        if "config_path" in locals() and config_path.exists():
            config_path.unlink()
        raise RuntimeError(f"Failed to create {linter} config: {str(e)}")

def build_linter_command(linter: str, config_path: Path, project_path: Path) -> list:
    """Build the command to run the specified linter."""
    project_path = project_path.resolve()  # Ensure absolute path
    
    if linter == Linter.RUFF:
        py_files = [str(f) for f in project_path.rglob("*.py")]
        if not py_files:
            return ["echo", "No Python files found"]
        return [
            "ruff",
            "check",
            *py_files,
            "--config",
            str(config_path),
            "--output-format=json"
        ]
    elif linter == Linter.PYLINT:
        py_files = [str(f) for f in project_path.rglob("*.py")]
        if not py_files:
            return ["echo", "No Python files found"]
        return [
            "pylint",
            "--rcfile",
            str(config_path),
            "--output-format=json",
            "--persistent=no",
            *py_files
        ]
    elif linter == Linter.BANDIT:
        return [
            "bandit",
            "-r",
            str(project_path),
            "-c",
            str(config_path),
            "-f",
            "json",
            "-n", "5"
        ]
    elif linter == Linter.RADON:
        py_files = [str(f) for f in project_path.rglob("*.py")]
        if not py_files:
            return ["echo", "No Python files found"]
        return [
            "radon",
            "cc",
            "-s",
            "-j",
            *py_files
        ]
    else:
        raise ValueError(f"Unknown linter: {linter}")

def detect_project_root(extracted_dir: Path) -> Path:
    """Find the actual Python project root in extracted files"""
    extracted_dir = extracted_dir.resolve()
    
    # First check for Python-specific project markers
    python_markers = [
        "pyproject.toml",
        "setup.py",
        "requirements.txt",
        "Pipfile",
        "setup.cfg",
        "__init__.py"
    ]
    
    for marker in python_markers:
        for path in extracted_dir.rglob(marker):
            return path.parent.resolve()
    
    # Fallback to any directory with Python files
    py_files = list(extracted_dir.rglob("*.py"))
    if py_files:
        return py_files[0].parent.resolve()
        
    return extracted_dir.resolve()

def detect_project_type(project_path: Path) -> str:
    """Detect project type based on file patterns"""
    project_path = project_path.resolve()
    markers = {
        ProjectType.WEB: {"requirements.txt", "pyproject.toml", "django", "flask", "fastapi"},
        ProjectType.EMBEDDED: {"platformio.ini", "Makefile", ".ino", ".c", "micropython"},
        ProjectType.SECURITY: {"auth", "crypto", "security", "jwt", "oauth"}
    }
    
    scores = {pt: 0 for pt in ProjectType}
    for item in project_path.rglob("*"):
        if item.is_file():
            content = item.read_text(errors="ignore").lower() if item.suffix == ".py" else ""
            for pt, patterns in markers.items():
                if any(
                    (p in item.name.lower()) or
                    (p in str(item.relative_to(project_path)).lower()) or
                    (p.isalpha() and p in content)
                    for p in patterns
                ):
                    scores[pt] += 1
    
    if max(scores.values()) == 0:
        return ProjectType.UNKNOWN
    return max(scores.items(), key=lambda x: x[1])[0]

def generate_flamingo_message(issue: dict) -> str:
    """Generate a user-friendly message for a linter issue."""
    return f"[{issue.get('type', '').capitalize()}] {issue.get('code', '')}: {issue.get('message', '')}"

def parse_linter_output(output: str, linter: str, base_path: Path) -> List[Dict[str, Any]]:
    """Parse linter output into standardized format.
    
    Args:
        output: Raw linter output string
        linter: Linter name (e.g., 'radon', 'ruff')
        base_path: Base directory for relative file paths
        
    Returns:
        List of standardized issue dictionaries
    """
    if not output.strip():
        return []

    base_path = base_path.resolve()
    
    try:
        # Special case: Empty RUFF output
        if linter == Linter.RUFF and output.strip() == "[]":
            return []
            
        # Special handling for Radon
        if linter == Linter.RADON:
            try:
                # Normalize Radon output to always be a list of file results
                if output.startswith("{"):
                    data = [json.loads(output)]  # Single file -> wrap in list
                elif output.startswith("["):
                    data = json.loads(output)   # Multi-file (already list)
                else:
                    # Fallback for line-delimited JSON (unlikely for Radon)
                    data = [json.loads(line) for line in output.splitlines() if line.strip()]
                
                # Ensure we have a list (even if empty)
                if not isinstance(data, list):
                    data = [data] if data else []
                
                return _parse_radon_output(data, base_path)
            except (json.JSONDecodeError, TypeError) as e:
                logger.error(f"Failed to parse Radon output: {e}\nOutput: {output[:200]}...")
                return []
        logger.info(f"Raw Radon output: {output[:1000]}")  # Log first 1000 chars

        # Standard linter processing
        linter_type = {
            "ruff": LinterType.RUFF,
            "pylint": LinterType.PYLINT,
            "bandit": LinterType.BANDIT,
            "radon": LinterType.RADON
        }.get(linter.lower(), LinterType.RUFF)
        
        issues = parse_linter_output_service(output, linter_type, base_path)
        
        return [{
            "type": issue["type"].value,
            "file": issue["file"],
            "line": issue["line"],
            "message": issue["message"],
            "code": issue["code"],
            "url": issue.get("url", ""),
            "flamingo_message": generate_flamingo_message({
                "code": issue["code"],
                "message": issue["message"],
                "type": issue["type"].value
            })
        } for issue in issues]
        
    except Exception as e:
        logger.error(f"Error parsing {linter} output: {e}\nOutput was:\n{output[:200]}...")
        return []

def _parse_radon_output(data: List[Dict[str, Any]], base_path: Path) -> List[Dict[str, Any]]:
    """Convert Radon's complexity data to standard issues.
    
    Args:
        data: List of Radon file results (each containing 'filename' and 'results')
        base_path: Base directory for relative paths
        
    Returns:
        List of standardized issue dictionaries
    """
    issues = []
    
    for file_data in data:
        if not isinstance(file_data, dict):
            continue
            
        try:
            filename = file_data.get("filename", "")
            if not filename:
                continue
                
            relative_path = str(Path(filename).relative_to(base_path))
            
            for result in file_data.get("results", []):
                if not all(k in result for k in ["type", "name", "complexity"]):
                    continue
                    
                issues.append({
                    "type": LinterType.RADON.value,
                    "file": relative_path,
                    "line": result.get("lineno", 1),
                    "message": (
                        f"Cyclomatic complexity {result['complexity']} "
                        f"in {result['type']} '{result['name']}'"
                    ),
                    "code": f"RADON-{result.get('rank', 'UNKNOWN')}",
                    "url": "https://radon.readthedocs.io/en/latest/",
                    "severity": _get_radon_severity(result["complexity"])
                })
        except Exception as e:
            logger.warning(f"Skipping invalid Radon data in {filename}: {e}")
            continue
            
    return issues


def _get_radon_severity(complexity: int) -> str:
    """Map Radon complexity score to severity levels."""
    if complexity > 20:
        return "critical"
    elif complexity > 10:
        return "high"
    elif complexity > 5:
        return "medium"
    return "low"

def _parse_radon_file_data(file_data: Dict[str, Any], rel_path: str) -> List[Dict[str, Any]]:
    """Parse Radon file data into issues"""
    issues = []
    
    # Handle methods
    for method in file_data.get('methods', []):
        issues.append({
            "type": "complexity",
            "file": rel_path,
            "line": method['lineno'],
            "message": f"Method '{method['name']}' has complexity {method['complexity']}",
            "code": f"RADON-M{method['complexity']}",
            "linter": "radon"
        })
    
    # Handle classes
    for cls in file_data.get('classes', []):
        issues.append({
            "type": "complexity",
            "file": rel_path,
            "line": cls['lineno'],
            "message": f"Class '{cls['name']}' has complexity {cls['complexity']}",
            "code": f"RADON-C{cls['complexity']}",
            "linter": "radon"
        })
    
    return issues

async def run_single_linter(linter: str, project_path: Path) -> Dict[str, Any]:
    """Run an individual linter and return results"""
    try:
        project_path = project_path.resolve()
        logger.info(f"Running {linter} analysis in: {project_path}")
        
        # Find all Python files recursively
        py_files = list(project_path.rglob("*.py"))
        logger.info(f"Found {len(py_files)} Python files:")
        for py_file in py_files:
            logger.info(f"- {py_file.relative_to(project_path)}")
        
        if not py_files and linter != Linter.RADON:
            return {
                "success": True,
                "output": "No Python files found",
                "issues": [],
                "raw_stderr": ""
            }

        # Build linter command
        config_path = setup_linter_config(linter)
        cmd = build_linter_command(linter, config_path, project_path)
        
        logger.info(f"Executing: {' '.join(cmd)}")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(project_path),
            timeout=300
        )
        
        # Special handling for Ruff's success case
        if linter == Linter.RUFF and result.returncode != 0:
            if "All checks passed" in result.stderr:
                return {
                    "success": True,
                    "output": "[]",
                    "issues": [],
                    "raw_stderr": result.stderr
                }
        
        logger.debug(f"{linter} stdout: {result.stdout[:200]}...")
        if result.stderr:
            logger.warning(f"{linter} stderr: {result.stderr[:200]}...")
        
        # Parse output
        issues = parse_linter_output(result.stdout, linter, project_path)
        
        logger.info(f"{linter} analysis completed. Found {len(issues)} issues.")
        return {
            "success": True,
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
        logger.error(f"{linter} failed: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "raw_stderr": str(e)
        }

async def run_linter_analysis(project_path: Path, experience_level: str) -> Dict[str, Any]:
    """Run all appropriate linters for the project"""
    project_path = project_path.resolve()
    
    # Run all linters in parallel
    ruff_result, pylint_result, bandit_result, radon_result = await asyncio.gather(
        run_single_linter(Linter.RUFF, project_path),
        run_single_linter(Linter.PYLINT, project_path),
        run_single_linter(Linter.BANDIT, project_path),
        run_single_linter(Linter.RADON, project_path)
    )
    
    # Filter issues based on experience level
    if experience_level == "beginner":
        ruff_result["issues"] = [i for i in ruff_result.get("issues", []) 
                               if i.get("code", "").startswith(("E", "F", "W"))]
        pylint_result["issues"] = [i for i in pylint_result.get("issues", [])
                                 if i.get("type") in ("error", "warning")]
    
    return {
        "project_type": detect_project_type(project_path).value,
        "experience_level": experience_level,
        "result": {
            "ruff": ruff_result,
            "pylint": pylint_result,
            "bandit": bandit_result,
            "radon": radon_result
        }
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
async def analyze_zip(zip_file: UploadFile = File(...)):
    session_id = str(uuid.uuid4())
    temp_dir = Path(tempfile.mkdtemp(prefix=f"pink-coded-{session_id}-"))
    ACTIVE_SESSIONS[session_id] = str(temp_dir)
    
    try:
        # Save ZIP
        zip_path = temp_dir / "upload.zip"
        with zip_path.open("wb") as buffer:
            shutil.copyfileobj(zip_file.file, buffer)
        
        # Extract to upload directory
        upload_dir = temp_dir / "upload"
        upload_dir.mkdir()
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(upload_dir)
        
        # Find the actual project root
        project_path = detect_project_root(upload_dir)
        logger.info(f"Project structure in {project_path}:")
        for f in project_path.rglob("*"):
            logger.info(f"- {f.relative_to(project_path)}")
        
        # Run analysis
        result = await run_linter_analysis(project_path, "intermediate")
        ACTIVE_ANALYSES[session_id] = result
        
        return {
            **result,
            "session_id": session_id,
            "temp_dir": str(temp_dir)
        }
    except Exception as e:
        logger.error(f"ZIP analysis failed: {str(e)}", exc_info=True)
        raise HTTPException(500, detail=str(e))
        
@router.post("/generate-fix")
async def generate_fix(
    code: str = Body(...),
    issue: dict = Body(...),
    user_id: str = Body(...)
):
    """Generate a fix for a specific code issue"""
    try:
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
        
        # TODO: Replace with actual API call
        if issue.get('code') == 'D100':
            return {
                "fix": '"""Module docstring"""\n' + code,
                "explanation": "Added missing module docstring"
            }
        else:
            return {
                "fix": code,
                "explanation": "No automatic fix available for this issue type"
            }
            
    except Exception as e:
        logger.error(f"Fix generation failed: {e}", exc_info=True)
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
                result["main_analysis"]["issues"] = [
                    issue for issue in result["main_analysis"]["issues"] 
                    if issue["file"] != file_path
                ]
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
        logger.error(f"Analysis error: {str(e)}", exc_info=True)
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
        logger.error(f"Fix failed: {e}", exc_info=True)
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
        logger.error(f"Export failed: {e}", exc_info=True)
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