from typing import List, Dict, Any, Optional
import json
from pathlib import Path
from enum import Enum
from app.models import Issue
from pydantic import BaseModel

class Issue(BaseModel):
    """Standardized issue representation"""
    code: str
    message: str
    file: str
    line: int
    severity: str = "warning"
    linter: str = "unknown"

class LinterType(str, Enum):
    RUFF = "ruff"
    PYLINT = "pylint"
    BANDIT = "bandit"
    RADON = "radon"

class IssueSeverity(str, Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    SECURITY = "security"
    COMPLEXITY = "complexity"
    CONVENTION = "convention"
    REFACTOR = "refactor"

def parse_linter_output(
    output: str, 
    linter: LinterType,
    base_path: Optional[Path] = None
) -> List[Dict[str, Any]]:
    """
    Parse linter output into standardized format with explanations support
    
    Args:
        output: Raw linter output string
        linter: Type of linter (ruff/pylint/bandit/radon)
        base_path: Optional base path for relative file paths
        
    Returns:
        List of parsed issues with consistent structure
    """
    if not output.strip():
        return []

    try:
        if linter == LinterType.RUFF:
            return parse_ruff_output(output, base_path)
        elif linter == LinterType.PYLINT:
            return parse_pylint_output(output, base_path)
        elif linter == LinterType.BANDIT:
            return parse_bandit_output(output, base_path)
        elif linter == LinterType.RADON:
            return parse_radon_output(output, base_path)
        else:
            raise ValueError(f"Unsupported linter: {linter}")
    except Exception as e:
        print(f"Error parsing {linter} output: {str(e)}")
        return []

def parse_ruff_output(
    output: str, 
    base_path: Optional[Path] = None
) -> List[Dict[str, Any]]:
    """Parse Ruff JSON output into standardized format"""
    try:
        issues = json.loads(output)
        parsed = []
        
        for issue in issues:
            file_path = Path(issue["filename"])
            rel_path = str(file_path.relative_to(base_path)) if base_path else issue["filename"]
            
            parsed.append({
                "type": IssueSeverity.ERROR if issue["code"].startswith("E") 
                       else IssueSeverity.WARNING,
                "file": rel_path,
                "line": issue["location"]["row"],
                "column": issue["location"]["column"],
                "message": issue["message"],
                "code": issue["code"],
                "url": f"https://beta.ruff.rs/docs/rules/{issue['code'].lower()}/",
                "linter": LinterType.RUFF
            })
        return parsed
    except Exception as e:
        print(f"Ruff parse error: {str(e)}")
        return []

def parse_pylint_output(
    output: str, 
    base_path: Optional[Path] = None
) -> List[Dict[str, Any]]:
    """Parse Pylint JSON output into standardized format"""
    try:
        issues = json.loads(output)
        parsed = []
        
        for issue in issues:
            file_path = Path(issue["path"])
            rel_path = str(file_path.relative_to(base_path)) if base_path else issue["path"]
            
            # Map Pylint types to our severity levels
            severity = {
                "error": IssueSeverity.ERROR,
                "warning": IssueSeverity.WARNING,
                "convention": IssueSeverity.CONVENTION,
                "refactor": IssueSeverity.REFACTOR,
                "information": IssueSeverity.INFO
            }.get(issue["type"].lower(), IssueSeverity.INFO)
            
            parsed.append({
                "type": severity,
                "file": rel_path,
                "line": issue["line"],
                "column": issue.get("column", 0),
                "message": issue["message"],
                "code": issue["message-id"],
                "symbol": issue["symbol"],
                "linter": LinterType.PYLINT
            })
        return parsed
    except Exception as e:
        print(f"Pylint parse error: {str(e)}")
        return []

def parse_bandit_output(
    output: str,
    base_path: Optional[Path] = None
) -> List[Dict[str, Any]]:
    """Parse Bandit JSON output into standardized format"""
    try:
        data = json.loads(output)
        parsed = []
        
        for issue in data.get("results", []):
            file_path = Path(issue["filename"])
            rel_path = str(file_path.relative_to(base_path)) if base_path else issue["filename"]
            
            parsed.append({
                "type": IssueSeverity.SECURITY,
                "file": rel_path,
                "line": issue["line_number"],
                "column": 0,
                "message": issue["issue_text"],
                "code": issue["test_id"],
                "severity": issue["issue_severity"],
                "confidence": issue["issue_confidence"],
                "url": issue["more_info"],
                "linter": LinterType.BANDIT
            })
        return parsed
    except Exception as e:
        print(f"Bandit parse error: {str(e)}")
        return []

def parse_radon_output(
    output: str,
    base_path: Optional[Path] = None
) -> List[Dict[str, Any]]:
    """Parse Radon JSON output into standardized format"""
    try:
        issues = json.loads(output)
        parsed = []
        
        for file_result in issues:
            file_path = Path(file_result["filename"])
            rel_path = str(file_path.relative_to(base_path)) if base_path else file_result["filename"]
            
            # Process methods
            for method in file_result.get("methods", []):
                parsed.append({
                    "type": IssueSeverity.COMPLEXITY,
                    "file": rel_path,
                    "line": method["lineno"],
                    "column": 0,
                    "message": f"Method '{method['name']}' has high complexity ({method['complexity']})",
                    "code": f"RADON-M{method['complexity']}",
                    "complexity": method["complexity"],
                    "linter": LinterType.RADON
                })
            
            # Process classes
            for class_result in file_result.get("classes", []):
                parsed.append({
                    "type": IssueSeverity.COMPLEXITY,
                    "file": rel_path,
                    "line": class_result["lineno"],
                    "column": 0,
                    "message": f"Class '{class_result['name']}' has high complexity ({class_result['complexity']})",
                    "code": f"RADON-C{class_result['complexity']}",
                    "complexity": class_result["complexity"],
                    "linter": LinterType.RADON
                })
        return parsed
    except Exception as e:
        print(f"Radon parse error: {str(e)}")
        return []

def combine_issues(
    *issue_lists: List[List[Dict[str, Any]]]
) -> List[Dict[str, Any]]:
    """Combine multiple issue lists into one with consistent structure"""
    combined = []
    for issues in issue_lists:
        combined.extend(issues)
    return combined