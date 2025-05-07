#backend\app\routers\analysis.py 
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
            'target': ['*'],
            'recursive': True,
            'confidence': 'low',  # Changed from 'high'
            'severity': 'low',    # Changed from 'medium'
            'tests': [],  # Specific test IDs
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
                issue_type = "error" if issue["code"].startswith("E") else "warning"
                parsed.append({
                    "type": issue_type,
                    "file": rel_path,
                    "line": issue["location"]["row"],
                    "message": issue["message"],
                    "code": issue["code"],
                    "url": f"https://docs.astral.sh/ruff/rules/{issue['code'].lower()}"
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
                        "severity": issue["issue_severity"].lower(),  # Standardize to lowercase
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
    try:
        # Handle both raw JSON and stringified JSON
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
                    "code": f"RADON-{item.get('rank', 'U')}",  # 'U' for unknown rank
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
        
        # In run_single_linter() in analysis.py, before Bandit execution:
        py_files = list(project_path.rglob("*.py"))
        logger.info(f"Python files found: {len(py_files)}")
        for f in py_files[:3]:  # Log first 3 files
                logger.info(f"Sample file: {f}")

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
        logger.info(f"Bandit raw stdout:\n{result.stdout[:1000]}...")  # First 1000 chars
        logger.info(f"Bandit stderr:\n{result.stderr}")

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