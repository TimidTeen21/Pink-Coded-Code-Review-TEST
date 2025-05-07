# backend/app/services/explanation_engine.py
from typing import Dict, Any, Optional
import os
import google.generativeai as genai
import json
from pathlib import Path
from app.models import UserProfile, Issue
from dotenv import load_dotenv

load_dotenv()

class ExplanationEngine:
    def __init__(self, profile_service):
        self.profile_service = profile_service
        self.templates = self._load_templates()
        self.gemini, self.current_model = self._init_gemini()
        self.common_patterns = ['E', 'W', 'F', 'B', 'R']  # Common Python issue code prefixes
        self.current_model = None  # Track which model is being used

    def _init_gemini(self) -> tuple[Optional[genai.GenerativeModel], Optional[str]]:
        """Initialize and return (client, model_name) tuple"""
        try:
            if not (api_key := os.getenv('GEMINI_API_KEY')):
                print("Warning: GEMINI_API_KEY not found in environment")
                return None

            genai.configure(api_key=api_key)

            # Get available models
            available_models = [m.name for m in genai.list_models()]
            print(f"Available models: {available_models}")
            
            # Try latest models first, then fallback to older versions
            for model_name in [
                'models/gemini-2.5-pro-latest',
                'models/gemini-2.5-flash-latest',
                'models/gemini-1.5-pro-latest',
                'models/gemini-pro'
            ]:
                if model_name in available_models:
                    try:
                        model = genai.GenerativeModel(model_name)
                        # Test connection with simple prompt
                        model.generate_content("Test connection")
                        print(f"Using Gemini model: {model_name}")
                        return model, model_name
                    except Exception as e:
                        print(f"Failed to initialize {model_name}: {str(e)}")
                        continue
            print("No working Gemini models found")
            return None, None
    
        except Exception as e:
            print(f"Gemini initialization failed - {str(e)}")
            return None

    def _load_templates(self) -> Dict[str, Any]:
        """Load explanation templates with validation"""
        template_path = Path(__file__).parent / "explanation_templates.json"
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                templates = json.load(f)
                if 'generic' not in templates:
                    raise ValueError("Missing 'generic' template")
                return templates
        except (FileNotFoundError, ValueError) as e:
            print(f"Warning: Loading templates failed - {str(e)}")
            return {
                "generic": {
                    "beginner": {"why": "This is a problem.", "fix": "Do this to fix it."},
                    "intermediate": {"why": "This happens because...", "fix": "Try this solution..."},
                    "advanced": {"why": "Deep technical reason.", "fix": "Optimal fix."}
                }
            }

    def _get_template_for_level(self, issue: Issue, level: str) -> Optional[Dict[str, str]]:
        """Get template if exists, None otherwise"""
        return self.templates.get(issue.code, {}).get(level)

    def _is_common_issue(self, code: str) -> bool:
        """Check if code follows common Python issue patterns"""
        return any(code.startswith(prefix) for prefix in self.common_patterns)

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
                formatted[key] = text
        return formatted

    def _generate_gemini_explanation(self, issue: Issue, profile: UserProfile) -> Dict[str, str]:
        """Generate explanation using Gemini with enhanced error handling"""
        if not self.gemini:
            return {
                "why": "AI explanation service currently unavailable",
                "fix": "Please check back later or consult documentation",
                "source": "error"
            }

        prompt = f"""As a senior Python developer, explain this code issue to a {profile.experience_level} programmer:

**Rule**: {issue.code}
**Message**: {issue.message}
**File**: {issue.file}
**Line**: {issue.line}

Provide:
1. "Why this matters" - 1-2 sentence impact analysis
2. "How to fix" - {profile.experience_level}-appropriate solution
3. "Example" - Code snippet if applicable

Structure your response with these exact section headers:
### Why
### Fix
### Example"""

        try:
            response = self.gemini.generate_content(prompt, stream=False)
            text = response.text
            
            # Parse the structured response
            sections = {
                "why": self._extract_section(text, "Why"),
                "fix": self._extract_section(text, "Fix"),
                "example": self._extract_section(text, "Example"),
                "source": f"gemini-{self.current_model.split('/')[-1]}"
            }
            return sections
            
        except Exception as e:
            print(f"Gemini error ({self.current_model}): {str(e)}")
            return {
                "why": f"AI explanation failed (model: {self.current_model})",
                "fix": "Please consult the documentation for this issue",
                "source": "error"
            }

    def _extract_section(self, text: str, header: str) -> str:
        """Helper to parse structured response from Gemini"""
        start = text.find(f"### {header}")
        if start == -1:
            return f"No {header.lower()} explanation provided"
        
        start += len(f"### {header}") + 1
        end = text.find("###", start)
        return text[start:end].strip() if end != -1 else text[start:].strip()

    def explain(self, issue: Issue, user_id: str) -> Dict[str, str]:
        """Generate explanation with robust fallback logic"""
        profile = self.profile_service.get_profile(user_id)
        
        # 1. Try exact template match first
        if template := self._get_template_for_level(issue, profile.experience_level):
            explanation = self._format_template(template, issue)
            explanation["source"] = "template"
        
        # 2. For common Python patterns, use generic template
        elif self._is_common_issue(issue.code):
            explanation = self._format_template(
                self.templates['generic'][profile.experience_level],
                issue
            )
            explanation["source"] = "generic_template"
        
        # 3. For truly custom issues, use Gemini
        else:
            explanation = self._generate_gemini_explanation(issue, profile)
            # If Gemini failed, use a basic generic explanation
            if explanation["source"] == "error":
                explanation = self._format_template(
                    self.templates['generic'][profile.experience_level],
                    issue
                )
                explanation["source"] = "fallback"
        
        # Add personalized advice
        if "OOP" in profile.known_concepts and "fix" in explanation:
            explanation['fix'] += "\n\n(OOP Tip: Consider breaking this into smaller methods)"
        
        # Track usage
        self._track_issue_usage(user_id, issue.code)
        
        return {
            "title": f"{issue.code}: {issue.message}",
            "location": f"{issue.file}:{issue.line}",
            **explanation
        }

    def _track_issue_usage(self, user_id: str, issue_code: str):
        """Update usage statistics"""
        profile = self.profile_service.get_profile(user_id)
        profile.seen_issues[issue_code] = profile.seen_issues.get(issue_code, 0) + 1
        self.profile_service.save_profile(profile)