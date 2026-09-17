import google.generativeai as genai
from loguru import logger
from typing import List, Dict, Optional

from app.config import settings
from app.ai.prompts import SalesPrompts


class AIEngine:
    def __init__(self):
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-1.0-pro')
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
            response = self.model.generate_content(full_prompt)
            return response.text

        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return self.prompts.get_fallback_response(language)

    async def detect_language(self, text: str) -> str:
        try:
            prompt = f"Detect the language of this text. Reply with just the ISO 639-1 language code (e.g., 'en', 'es', 'fr'). Text: {text}"
            response = self.model.generate_content(prompt)
            return response.text.strip().lower()[:2]

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
            
            response = self.model.generate_content(prompt)
            
            import json
            import re
            json_match = re.search(r'\{[^}]+\}', response.text)
            if json_match:
                return json.loads(json_match.group())
            return {"intent": "browsing", "sentiment": "neutral", "urgency": "medium", "topics": []}

        except Exception as e:
            logger.error(f"Intent analysis error: {e}")
            return {"intent": "browsing", "sentiment": "neutral", "urgency": "medium", "topics": []}