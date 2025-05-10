# backend/app/services/deepseek_client.py
import os
import httpx

class DeepSeekClient:
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY not found in environment")
        
        self.base_url = "https://api.deepseek.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.timeout = httpx.Timeout(30.0)
        self.client = httpx.AsyncClient()

    async def generate_explanation(self, prompt: str) -> dict:
        payload = {
            "model": "deepseek-coder",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 1000
        }

        try:
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=self.headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            return self._parse_response(response.json())
        except httpx.HTTPStatusError as e:
            print(f"DeepSeek API error: {e.response.text}")
            return {}
        except Exception as e:
            print(f"DeepSeek connection error: {str(e)}")
            return {}

    def _parse_response(self, data: dict) -> dict:
        content = data["choices"][0]["message"]["content"]
        return {
            "why": self._extract_section(content, "Why"),
            "fix": self._extract_section(content, "Fix"),
            "example": self._extract_section(content, "Example"),
            "advanced_tip": self._extract_section(content, "ProTip")
        }

    def _extract_section(self, text: str, header: str) -> str:
        start = text.find(f"### {header}")
        if start == -1:
            return ""
        start += len(f"### {header}") + 1
        end = text.find("###", start)
        return text[start:end].strip() if end != -1 else text[start:].strip()