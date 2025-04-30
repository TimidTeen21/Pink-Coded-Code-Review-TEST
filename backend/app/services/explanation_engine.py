# backend/app/services/explanation_engine.py
from typing import Dict, Any
import json
from pathlib import Path
from app.models import UserProfile, Issue

class ExplanationEngine:
    def __init__(self, profile_service):
        self.profile_service = profile_service
        self.templates = self._load_templates()

    def _load_templates(self) -> Dict[str, Any]:
        """Load explanation templates from JSON file"""
        template_path = Path(__file__).parent / "explanation_templates.json"
        with open(template_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _get_template_for_level(self, issue: Issue, level: str) -> Dict[str, str]:
        """Get appropriate template for user's experience level"""
        # Try specific rule first, fall back to generic
        return (self.templates.get(issue.code, {}).get(level) or 
                self.templates['generic'][level])

    def _format_template(self, template: Dict[str, str], issue: Issue) -> Dict[str, str]:
        """Format template fields with issue details"""
        formatted = {}
        for key, text in template.items():
            try:
                formatted[key] = text.format(
                    code=issue.code,
                    message=issue.message,
                    file=issue.file,
                    line=issue.line,
                    severity=issue.severity
                )
            except KeyError:
                formatted[key] = text  # Use unformatted text if placeholders fail
        return formatted

    def explain(self, issue: Issue, user_id: str) -> Dict[str, str]:
        """Generate explanation for an issue"""
        profile = self.profile_service.get_profile(user_id)
        template = self._get_template_for_level(issue, profile.experience_level)
        explanation = self._format_template(template, issue)

        # Add concept-specific advice if available
        if "OOP" in profile.known_concepts:
            explanation['fix'] += "\n\nSince you know OOP: Consider refactoring into smaller methods."

        # Track seen issues
        profile.seen_issues[issue.code] = profile.seen_issues.get(issue.code, 0) + 1
        self.profile_service.save_profile(profile)
        
        return explanation