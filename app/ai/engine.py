from openai import AsyncOpenAI
from loguru import logger
from typing import List, Dict, Optional

from app.config import settings
from app.ai.prompts import SalesPrompts


class AIEngine:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        self.prompts = SalesPrompts()

    async def generate_response(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        products: List[Dict],
        language: str = "en"
    ) -> str:
        system_prompt = self.prompts.get_system_prompt(products, language)

        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(conversation_history[-10:])
        messages.append({"role": "user", "content": user_message})

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return self.prompts.get_fallback_response(language)

    async def detect_language(self, text: str) -> str:
        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "Detect the language of the text. Reply with just the ISO 639-1 language code (e.g., 'en', 'es', 'fr', 'de')."
                    },
                    {"role": "user", "content": text}
                ],
                temperature=0.1,
                max_tokens=5
            )

            return response.choices[0].message.content.strip().lower()

        except Exception as e:
            logger.error(f"Language detection error: {e}")
            return "en"

    async def analyze_intent(self, text: str) -> Dict:
        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": """Analyze the user message and return a JSON with:
                        - intent: (buying, browsing, asking, complaining, scheduling, handoff)
                        - sentiment: (positive, neutral, negative)
                        - urgency: (high, medium, low)
                        - topics: list of topics mentioned
                        Return only valid JSON."""
                    },
                    {"role": "user", "content": text}
                ],
                temperature=0.1
            )

            import json
            return json.loads(response.choices[0].message.content)

        except Exception as e:
            logger.error(f"Intent analysis error: {e}")
            return {
                "intent": "browsing",
                "sentiment": "neutral",
                "urgency": "medium",
                "topics": []
            }