#backend\app\routers\analysis.py from fastapi import APIRouter, HTTPException, UploadFile, File, Form
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
    def get_bandit_config():
        return {
            'target': ['*'],  # Scan everything
            'recursive': True,
            'confidence': 'high',  # Filter low-confidence findings
            'severity': 'medium',  # Minimum severity level
            'tests': ['*'],  # Include test files
            'skips': [],  # Don't skip any tests
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
    """Determine project type based on project files"""
    web_markers = {"requirements.txt", "pyproject.toml", "setup.py"}
    embedded_markers = {"platformio.ini", "Makefile"}
    security_markers = {"security", "auth", "crypto"}
    
    for item in project_path.iterdir():
        if any(marker in item.name.lower() for marker in security_markers):
            return ProjectType.SECURITY
            
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
                if linter == Linter.RUFF:
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
                elif linter == Linter.PYLINT:
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
                elif linter == Linter.BANDIT:
                    file_path = Path(issue["filename"])
                    rel_path = str(file_path.relative_to(base_path)) if file_path.is_absolute() else issue["filename"]
                    parsed.append({
                        "type": "security",
                        "file": rel_path,
                        "line": issue["line_number"],
                        "message": issue["issue_text"],
                        "code": issue["test_id"],
                        "url": issue["more_info"],
                        "severity": issue["issue_severity"].upper()
                    })
            except (ValueError, KeyError) as e:
                logger.warning(f"Skipping malformed issue: {e}")
                continue
                
        return parsed
    except Exception as e:
        logger.error(f"Error parsing {linter} output: {e}")
        return []

def parse_radon_output(output: str, base_path: Path) -> List[Dict[str, Any]]:
    """Parse radon complexity output into standardized format"""
    try:
        # Handle both string and pre-parsed JSON
        if isinstance(output, str):
            if not output.strip():
                return []
            results = json.loads(output)
        else:
            results = output
            
        issues = []
        for file_result in results:
            file_path = Path(file_result["filename"])
            rel_path = str(file_path.relative_to(base_path)) if file_path.is_absolute() else file_result["filename"]
            
            for method in file_result.get("methods", []):
                issues.append({
                    "type": "complexity",
                    "file": rel_path,
                    "line": method["lineno"],
                    "message": f"Method '{method['name']}' complexity {method['complexity']}",
                    "code": f"RADON-M{method['complexity']}",
                    "url": "https://radon.readthedocs.io/en/latest/intro.html"
                })
                
            for class_result in file_result.get("classes", []):
                issues.append({
                    "type": "complexity",
                    "file": rel_path,
                    "line": class_result["lineno"],
                    "message": f"Class '{class_result['name']}' complexity {class_result['complexity']}",
                    "code": f"RADON-C{class_result['complexity']}",
                    "url": "https://radon.readthedocs.io/en/latest/intro.html"
                })
                
        return issues
    except Exception as e:
        logger.error(f"Error parsing radon output: {e}")
        return []

async def run_single_linter(linter: str, project_path: Path) -> Dict[str, Any]:
    """Run an individual linter and return results"""
    try:
        logger.info(f"Running {linter} analysis in: {project_path}")
        
        if linter != Linter.RADON:
            if not list(project_path.rglob("*.py")):
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
            timeout=300  # Increased timeout for large projects
        )

        # Handle success codes
        success = True
        if linter == Linter.RUFF:
            success = result.returncode in [0, 4]
        elif linter == Linter.BANDIT:
            success = result.returncode in [0, 1]
        else:
            success = result.returncode == 0

        # Parse output
        issues = []
        if linter == Linter.RADON:
            issues = parse_radon_output(result.stdout, project_path)
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

async def run_linter_analysis(project_path: Path) -> Dict[str, Any]:
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
    
    # Always run complexity analysis
    radon_result = await run_single_linter(Linter.RADON, project_path)
    
    return {
        "project_type": project_type,
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
            
            if not zipfile.is_zipfile(zip_path):
                raise HTTPException(400, "Invalid ZIP file format")
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_path)
            
            result = await run_linter_analysis(temp_path)
            return result
            
        except zipfile.BadZipFile:
            raise HTTPException(400, "Invalid ZIP file format")
        except Exception as e:
            logger.error(f"ZIP analysis failed: {e}")
            raise HTTPException(500, f"Analysis failed: {e}")

@router.get("/debug-config")
async def debug_config():
    """Debug endpoint to check active linter configs"""
    configs = {}
    for linter in [Linter.RUFF, Linter.PYLINT, Linter.BANDIT]:
        config_path = setup_linter_config(linter)
        if config_path.exists():
            configs[linter] = config_path.read_text()
    return configs