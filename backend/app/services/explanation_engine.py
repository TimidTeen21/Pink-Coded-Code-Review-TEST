# backend/app/services/explanation_engine.py
from typing import Dict, Optional, Literal, Any
import os
import json
import logging
from pathlib import Path
from dotenv import load_dotenv
from app.models import UserProfile, Issue
import asyncio
from datetime import datetime
import time
import httpx  # For DeepSeek API calls

load_dotenv()

logger = logging.getLogger(__name__)

ExperienceLevel = Literal["beginner", "intermediate", "advanced"]

class RateLimiter:
    def __init__(self, calls, period):
        self.calls = calls
        self.period = period
        self.timestamps = []
    
    async def __call__(self, func):
        now = time.time()
        self.timestamps = [t for t in self.timestamps if t > now - self.period]
        
        if len(self.timestamps) >= self.calls:
            sleep_time = self.period - (now - self.timestamps[0])
            await asyncio.sleep(sleep_time)
            
        self.timestamps.append(time.time())
        return await func

class ExplanationEngine:
    def __init__(self, profile_service):
        self.profile_service = profile_service
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.api_url = "https://api.deepseek.ai/v1/chat/completions"  # Example endpoint
        self.templates = self._load_templates()
        self.common_patterns = ['E', 'W', 'F', 'B', 'R']
        self.explanation_cache = {}
        self.fallback_count = 0
        self.last_api_error = None
        self.client = httpx.AsyncClient(timeout=15.0)

    def _load_templates(self) -> Dict[str, Any]:
        """Load and validate explanation templates with backup"""
        template_path = Path(__file__).parent / "explanation_templates.json"
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                templates = json.load(f)
                
                required_levels = {"beginner", "intermediate", "advanced"}
                if not all(level in templates.get("generic", {}) for level in required_levels):
                    raise ValueError("Missing required experience levels")
                    
                # Validate each template has required fields
                for code, levels in templates.items():
                    if code != "generic":
                        for level in levels.values():
                            if not all(key in level for key in ["why", "fix"]):
                                raise ValueError(f"Template {code} missing required fields")
                
                return templates
        except Exception as e:
            logger.error(f"Template loading failed: {str(e)}")
            return self._create_fallback_templates()

    def _create_fallback_templates(self) -> Dict[str, Any]:
        """Generate emergency fallback templates"""
        return {
            "generic": {
                "beginner": {
                    "why": "This issue needs attention.",
                    "fix": "Consult documentation or a senior developer."
                },
                "intermediate": {
                    "why": "This indicates a potential problem.",
                    "fix": "Review best practices for this pattern."
                },
                "advanced": {
                    "why": "Technical deep dive would be required.",
                    "fix": "Analyze implementation details."
                }
            }
        }

    
    def _create_error_response(self, issue: Issue, error: str) -> Dict[str, str]:
        """Standard error response format"""
        return {
            "title": f"{issue.code}: {issue.message}",
            "location": f"{issue.file}:{issue.line}",
            "why": f"Explanation service error: {error}",
            "fix": "Please try again later or check API status",
            "source": "error",
            "error": error
        }
    
    rate_limiter = RateLimiter(calls=50, period=60)

    @rate_limiter
    async def _call_deepseek(self, prompt):
        return await self.deepseek.generate(prompt)

    async def generate_explanation(self, issue: Issue, user_id: str) -> Dict[str, str]:
        """Main entry point with enhanced error handling"""
        cache_key = f"{user_id}-{issue.code}-{issue.message[:50]}"
        
        try:
            # Check cache first
            if cached := self.explanation_cache.get(cache_key):
                if datetime.now().timestamp() - cached.get("_timestamp", 0) < 3600:  # 1 hour cache
                    return cached
            
            profile = self.profile_service.get_profile(user_id)
            explanation = await self._generate_with_timeout(issue, profile)
            
            if explanation.get("source") != "error":
                explanation["_timestamp"] = datetime.now().timestamp()
                self.explanation_cache[cache_key] = explanation
            
            return explanation
        except Exception as e:
            logger.error(f"Explanation generation failed: {str(e)}")
            return self._create_error_response(issue, str(e))
        
    async def _generate_with_timeout(self, issue: Issue, profile: UserProfile) -> Dict[str, str]:
        """Wrapper with timeout protection"""
        try:
            return await asyncio.wait_for(
                self._generate_explanation(issue, profile),
                timeout=15.0
            )
        except asyncio.TimeoutError:
            logger.error("Explanation generation timed out")
            return self._create_error_response(issue, "Request timed out")

    async def _generate_explanation(self, issue: Issue, profile: UserProfile) -> Dict[str, str]:
        """Explanation generation pipeline"""
        try:
            # 1. Try exact template match
            if template := self._get_template(issue.code, profile.experience_level):
                logger.debug(f"Using template for {issue.code}")
                return self._format_template(template, issue, "template")
            
            # 2. Try generic template for common patterns
            if self._is_common_issue(issue.code):
                logger.debug(f"Using generic template for {issue.code}")
                return self._format_template(
                    self.templates["generic"][profile.experience_level],
                    issue,
                    "generic_template"
                )
            
            # 3. Use DeepSeek for custom issues
            logger.debug(f"Requesting DeepSeek explanation for {issue.code}")
            deepseek_explanation = await self._generate_deepseek_explanation(issue, profile)
            if deepseek_explanation.get("source") != "error":
                return deepseek_explanation
            
            # 4. Final fallback
            self.fallback_count += 1
            logger.warning(f"Using fallback for {issue.code}")
            return self._format_template(
                self.templates["generic"][profile.experience_level],
                issue,
                "fallback"
            )
        except Exception as e:
            logger.error(f"Explanation generation error: {str(e)}")
            return self._create_error_response(issue, str(e))
        
    async def _generate_deepseek_explanation(self, issue: Issue, profile: UserProfile) -> Dict[str, str]:
        """Generate explanation using DeepSeek API"""
        prompt = self._build_deepseek_prompt(issue, profile)
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "You are a Python code analysis assistant."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7 if profile.experience_level == "advanced" else 0.3,
                "max_tokens": 1000
            }
            
            start_time = datetime.now()
            response = await self.client.post(self.api_url, json=payload, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            latency = (datetime.now() - start_time).total_seconds()
            logger.info(f"DeepSeek response received in {latency:.2f}s")
            
            content = data['choices'][0]['message']['content']
            parsed = self._parse_deepseek_response(content)
            
            if not parsed.get("why") or not parsed.get("fix"):
                raise ValueError("Incomplete response from DeepSeek")
                
            return {
                "title": f"{issue.code}: {issue.message}",
                "location": f"{issue.file}:{issue.line}",
                **parsed,
                "source": "deepseek-chat",
                "_latency": latency
            }
        except Exception as e:
            self.last_api_error = str(e)
            logger.error(f"DeepSeek API failed: {str(e)}")
            return {"source": "error", "error": str(e)}


    def _build_deepseek_prompt(self, issue: Issue, profile: UserProfile) -> str:
        return f"""Analyze this Python code issue and provide:

1. Impact Analysis (Why this matters for {profile.experience_level} developers)
2. Recommended Fix (Provide {profile.experience_level}-level solution)
3. Code Example (Show corrected implementation)
4. Best Practices (Relevant Python guidelines)

Issue Details:
- File: {issue.file}
- Line: {issue.line}
- Error: {issue.code} - {issue.message}

Format your response with clear section headings:
### Why
### Fix
### Example
### Best Practices"""

    def _parse_deepseek_response(self, text: str) -> Dict[str, str]:
        """Extract structured sections from DeepSeek's response"""
        sections = {
            "why": self._extract_section(text, "Why"),
            "fix": self._extract_section(text, "Fix"),
            "example": self._extract_section(text, "Example"),
            "best_practices": self._extract_section(text, "Best Practices")
        }
        return {k: v for k, v in sections.items() if v}
    
    def _extract_section(self, text: str, header: str) -> str:
        """Helper to parse section from structured response"""
        start = text.find(f"### {header}")
        if start == -1:
            return ""
        start += len(f"### {header}") + 1
        end = text.find("###", start)
        return text[start:end].strip() if end != -1 else text[start:].strip()

    def _get_template(self, issue_code: str, level: ExperienceLevel) -> Optional[Dict[str, str]]:
        """Get matching template if exists"""
        return self.templates.get(issue_code, {}).get(level)

    def _is_common_issue(self, code: str) -> bool:
        """Check if issue follows common patterns"""
        return any(code.startswith(prefix) for prefix in self.common_patterns)

    def _format_template(self, template: Dict[str, str], issue: Issue, source: str) -> Dict[str, str]:
        """Format template with issue details"""
        formatted = {
            "title": f"{issue.code}: {issue.message}",
            "location": f"{issue.file}:{issue.line}",
            "source": source
        }
        
        for key, text in template.items():
            try:
                formatted[key] = text.format(
                    code=issue.code,
                    message=issue.message,
                    file=issue.file,
                    line=issue.line,
                    severity=getattr(issue, 'severity', 'unknown')
                )
            except (KeyError, AttributeError):
                formatted[key] = text
                
        return formatted

    async def generate_contextual_fix(self, issue: Issue, code_snippet: str) -> str:
        """Generate a code fix using DeepSeek"""
        prompt = f"""Fix this Python issue for production code:
        - Error: {issue.message} ({issue.code})
        - Code Context:
        ```python
        {code_snippet}
        ```
        
        Provide ONLY the corrected code between ```python``` blocks.
        Include brief comments explaining key changes if significant."""
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "You are a Python code fix assistant."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.5,
                "max_tokens": 1000
            }
            
            response = await self.client.post(self.api_url, json=payload, headers=headers)
            response.raise_for_status()
            
            content = response.json()['choices'][0]['message']['content']
            
            # Extract code block
            start = content.find("```python")
            if start == -1:
                return code_snippet
                
            start += len("```python")
            end = content.find("```", start)
            return content[start:end].strip() if end != -1 else content[start:].strip()
            
        except Exception as e:
            logger.error(f"Contextual fix generation failed: {str(e)}")
            return code_snippet

    async def close(self):
        """Clean up resources"""
        await self.client.aclose()