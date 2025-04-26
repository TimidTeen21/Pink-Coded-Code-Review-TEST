# app/services/linter_selector.py
from typing import Literal

def get_linter_for_project(project_type: Literal["web", "embedded", "unknown"]) -> str:
    """Select appropriate linter based on project type"""
    linter_map = {
        "web": "ruff",
        "embedded": "pylint",
        "unknown": "ruff"  # default fallback
    }
    return linter_map.get(project_type.lower(), "ruff")