import httpx
from loguru import logger
from typing import List, Dict, Optional

from app.config import settings
from app.ai.prompts import SalesPrompts


class AIEngine:
    def __init__(self):
        self.api_key = settings.gemini_api_key
        self.model = 'gemini-1.5-flash'
        self.base_url = 'https://generativelanguage.googleapis.com/v1beta'
        self.prompts = SalesPrompts()

    async def generate_response(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        products: List[Dict],
        language: str = "en"
    ) -> str:
        system_prompt = self.prompts.get_system_prompt(products, language)

        history_text = ""
        for msg in conversation_history[-10:]:
            role = "Customer" if msg["role"] == "user" else "Assistant"
            history_text += f"{role}: {msg['content']}\n"

        full_prompt = f"""{system_prompt}

Previous Conversation:
{history_text}

Customer: {user_message}

Assistant:"""

        try:
            url = f"{self.base_url}/models/{self.model}:generateContent?key={self.api_key}"
            payload = {
                "contents": [{
                    "parts": [{"text": full_prompt}]
                }]
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, timeout=30.0)
                data = response.json()
                
                if "candidates" in data and len(data["candidates"]) > 0:
                    return data["candidates"][0]["content"]["parts"][0]["text"]
                else:
                    logger.error(f"Gemini API error: {data}")
                    return self.prompts.get_fallback_response(language)

        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return self.prompts.get_fallback_response(language)

    async def detect_language(self, text: str) -> str:
        try:
            prompt = f"Detect the language of this text. Reply with just the ISO 639-1 language code (e.g., 'en', 'es', 'fr'). Text: {text}"
            
            url = f"{self.base_url}/models/{self.model}:generateContent?key={self.api_key}"
            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }]
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, timeout=10.0)
                data = response.json()
                
                if "candidates" in data and len(data["candidates"]) > 0:
                    return data["candidates"][0]["content"]["parts"][0]["text"].strip().lower()[:2]
            return "en"

        except Exception as e:
            logger.error(f"Language detection error: {e}")
            return "en"

    async def analyze_intent(self, text: str) -> Dict:
        try:
            prompt = f"""Analyze this message and return ONLY a JSON object with these fields:
- intent: (buying, browsing, asking, complaining, scheduling, handoff)
- sentiment: (positive, neutral, negative)
- urgency: (high, medium, low)
- topics: list of topics mentioned

Message: {text}"""
            
            url = f"{self.base_url}/models/{self.model}:generateContent?key={self.api_key}"
            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }]
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, timeout=10.0)
                data = response.json()
                
                if "candidates" in data and len(data["candidates"]) > 0:
                    text = data["candidates"][0]["content"]["parts"][0]["text"]
                    import json
                    import re
                    json_match = re.search(r'\{[^}]+\}', text)
                    if json_match:
                        return json.loads(json_match.group())
            
            return {"intent": "browsing", "sentiment": "neutral", "urgency": "medium", "topics": []}

        except Exception as e:
            logger.error(f"Intent analysis error: {e}")
            return {"intent": "browsing", "sentiment": "neutral", "urgency": "medium", "topics": []}