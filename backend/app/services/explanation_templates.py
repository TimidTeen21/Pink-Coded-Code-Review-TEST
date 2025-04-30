import json
from pathlib import Path
from typing import Dict, Literal

ExperienceLevel = Literal["beginner", "intermediate", "advanced"]

class ExplanationTemplates:
    def __init__(self):
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict:
        template_path = Path(__file__).parent / "explanation_templates.json"
        with open(template_path) as f:
            return json.load(f)
    
    def get_template(self, issue_code: str, level: ExperienceLevel = "intermediate") -> Dict:
        try:
            return self.templates.get(issue_code, {}).get(level, self.templates["generic"][level])
        except KeyError:
            return {
                "error": f"No template found for {issue_code} at {level} level",
                "title": "Explanation not available",
                "description": "Please check back later"
            }
        
        