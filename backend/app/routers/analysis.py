from fastapi import APIRouter, HTTPException, UploadFile, File, Form
import subprocess
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
import os

router = APIRouter(prefix="/api/v1/analysis", tags=["analysis"])

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnalysisRequest(BaseModel):
    project_path: str
    project_type: Optional[str] = None
    linter: Optional[str] = None

class ProjectType(str, Enum):
    WEB = "web"
    EMBEDDED = "embedded"
    UNKNOWN = "unknown"

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

def setup_linter_config(linter: str) -> Path:
    """Create temporary linter configuration file"""
    config_dir = Path("/tmp/pink-coded-config")
    config_dir.mkdir(exist_ok=True)
    
    if linter == "ruff":
        config_path = config_dir / "ruff.toml"
        with open(config_path, "w") as f:
            toml.dump(LinterConfig.get_ruff_config(), f)
    else:
        config_path = config_dir / ".pylintrc"
        parser = configparser.ConfigParser()
        parser.read_dict(LinterConfig.get_pylint_config())
        parser.write(config_path.open("w"))
    
    return config_path

def detect_project_type(project_path: Path) -> str:
    """Determine project type based on project files"""
    web_markers = {"requirements.txt", "pyproject.toml", "setup.py"}
    embedded_markers = {"platformio.ini", "Makefile"}
    
    for marker in web_markers:
        if (project_path / marker).exists():
            return ProjectType.WEB
    
    for marker in embedded_markers:
        if (project_path / marker).exists():
            return ProjectType.EMBEDDED
    
    return ProjectType.UNKNOWN

def parse_linter_output(output: str, linter: str, base_path: Path) -> List[Dict[str, Any]]:
    """Parse linter output into standardized format"""
    if not output.strip():
        return []
    
    try:
        issues = json.loads(output)
        parsed = []
        
        for issue in issues:
            try:
                # Handle both Ruff and Pylint output formats
                if linter == "ruff":
                    file_path = Path(issue["filename"])
                    rel_path = str(file_path.relative_to(base_path)) if file_path.is_absolute() else issue["filename"]
                    issue_type = "error" if issue["code"].startswith("E") else "warning"
                    parsed.append({
                        "type": issue_type,
                        "file": rel_path,
                        "line": issue["location"]["row"],
                        "message": issue["message"],
                        "code": issue["code"],
                        "url": f"https://docs.astral.sh/ruff/rules/{issue['code'].lower()}"
                    })
                else:  # Pylint
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
            except (ValueError, KeyError) as e:
                logger.warning(f"Skipping malformed issue: {e}")
                continue
                
        return parsed
    except Exception as e:
        logger.error(f"Error parsing {linter} output: {e}")
        return []

async def run_linter(linter: str, project_path: Path) -> Dict[str, Any]:
    try:
        logger.info(f"Starting analysis in: {project_path}")
        
        # Verify Python files exist
        py_files = list(project_path.rglob("*.py"))
        if not py_files:
            logger.warning("No Python files found in project")
            return {
                "success": True,  # Changed from False to True for empty projects
                "output": "No Python files found",
                "errors": [],
                "raw_stderr": ""
            }

        config_path = setup_linter_config(linter)
        
        cmd = [
            "ruff",
            "check",
            "--config", str(config_path),
            "--output-format=json",
            "--no-cache",
            str(project_path)
        ] if linter == "ruff" else [
            "pylint",
            f"--rcfile={config_path}",
            "--output-format=json",
            "--recursive=y",
            str(project_path)
        ]

        logger.info(f"Executing: {' '.join(cmd)}")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(project_path),
            timeout=30
        )

        # Ruff returns 0 (success) even when it finds issues
        success = result.returncode in [0, 4]  # 0=no issues, 4=issues found
        
        # Parse the output regardless of return code
        errors = parse_linter_output(result.stdout, linter, project_path)
        
        logger.info(f"Analysis completed. Found {len(errors)} issues.")
        return {
            "success": True,  # Always return True since we want to show results even with issues
            "output": result.stdout,
            "errors": errors,
            "raw_stderr": result.stderr
        }

    except subprocess.TimeoutExpired:
        logger.error("Analysis timed out")
        return {
            "success": False,
            "error": "Analysis timed out",
            "raw_stderr": "Process exceeded 30 second limit"
        }
    except Exception as e:
        logger.error(f"Linter failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "raw_stderr": str(e)
        }

@router.post("/analyze-zip")
async def analyze_zip(zip_file: UploadFile = File(...)):
    """Process uploaded ZIP file"""
    with tempfile.TemporaryDirectory(prefix="pink-coded-") as temp_dir:
        try:
            temp_path = Path(temp_dir)
            zip_path = temp_path / "upload.zip"
            
            # Save and extract
            with zip_path.open("wb") as buffer:
                shutil.copyfileobj(zip_file.file, buffer)
            
            # Verify ZIP contents
            if not zipfile.is_zipfile(zip_path):
                raise HTTPException(400, "Invalid ZIP file format")
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_path)
            
            # Analyze
            project_type = detect_project_type(temp_path)
            result = await run_linter("ruff" if project_type == ProjectType.WEB else "pylint", temp_path)
            
            return {
                "project_type": project_type,
                "linter": "ruff" if project_type == ProjectType.WEB else "pylint",
                "analysis": result
            }
            
        except zipfile.BadZipFile:
            raise HTTPException(400, "Invalid ZIP file format")
        except Exception as e:
            logger.error(f"ZIP analysis failed: {e}")
            raise HTTPException(500, f"Analysis failed: {e}")

@router.post("/full-analysis")
async def full_analysis(request: AnalysisRequest):
    """Legacy path-based analysis endpoint"""
    try:
        project_path = Path(request.project_path)
        if not project_path.exists():
            raise HTTPException(404, "Project path not found")
            
        project_type = request.project_type or detect_project_type(project_path)
        result = await run_linter(request.linter or ("ruff" if project_type == ProjectType.WEB else "pylint"), project_path)
        
        return {
            "project_type": project_type,
            "linter": "ruff" if project_type == ProjectType.WEB else "pylint",
            "analysis": result
        }
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(500, f"Analysis failed: {e}")

@router.get("/debug-config")
async def debug_config():
    """Debug endpoint to check active linter configs"""
    configs = {}
    for linter in ["ruff", "pylint"]:
        config_path = setup_linter_config(linter)
        if config_path.exists():
            configs[linter] = config_path.read_text()
    return configs