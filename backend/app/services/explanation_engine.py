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
        prompt = f"""Generate a {profile.experience_level}-friendly explanation for this issue:
        
        **Code**: {issue.code}
        **Message**: {issue.message}
        **File**: {issue.file}:{issue.line}
        **Severity**: {issue.severity}

        Structure your response with these sections:
        1. "Why" - Impact analysis
        2. "Fix" - Actionable solution (bullet points)
        3. "Example" - Code snippet (if applicable)
        4. "Advanced Tip" - Optional deeper context

        Adapt your response for a {profile.experience_level} developer.
        """

        try:
            response = self.gemini.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.3 if profile.experience_level == "beginner" else 0.7,
                    "max_output_tokens": 500
                }
            )
            return self._parse_gemini_response(response.text)
        except Exception as e:
            logger.error(f"Gemini failed: {str(e)}")
            return self._get_fallback_explanation(issue, profile)

    def _parse_gemini_response(self, text: str) -> Dict[str, str]:
        sections = ["why", "fix", "example", "advanced_tip"]
        parsed = {}
        for section in sections:
            start = text.lower().find(f"{section}:")
            if start == -1:
                parsed[section] = ""
                continue
            start += len(section) + 1
            end = text.find("\n\n", start)
            parsed[section] = text[start:end].strip() if end != -1 else text[start:].strip()
        return parsed
    
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