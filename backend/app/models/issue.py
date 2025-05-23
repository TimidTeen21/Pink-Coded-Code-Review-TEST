# backend/app/models/issue.py
from pydantic import BaseModel
from typing import Dict, Optional, Literal
from enum import Enum

class IssueType(str, Enum):
    ERROR = "error"
    WARNING = "warning"
    SECURITY = "security"
    COMPLEXITY = "complexity"

class Issue(BaseModel):
    type: IssueType
    file: str
    line: int
    message: str
    code: str
    url: Optional[str] = None
    flamingo_message: Optional[str] = None
    explanation: Optional[Dict[str, str]] = None
    severity: Optional[Literal["low", "medium", "high"]] = None
    confidence: Optional[Literal["low", "medium", "high"]] = None