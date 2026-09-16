from typing import List, Dict

from app.config import settings


class SalesPrompts:
    def get_system_prompt(self, products: List[Dict], language: str = "en") -> str:
        products_text = self._format_products(products)

        language_instructions = self._get_language_instructions(language)

        return f"""You are an expert AI sales agent for {settings.business_name}.
Your role is to help customers find the perfect products, answer their questions,
and guide them through the purchase process.

{language_instructions}

BUSINESS HOURS:
- Operating hours: {settings.business_hours_start} to {settings.business_hours_end} {settings.business_timezone}
- Phone: {settings.business_phone}
- Email: {settings.business_email}

AVAILABLE PRODUCTS:
{products_text}

YOUR RESPONSIBILITIES:
1. Greet customers warmly and professionally
2. Understand their needs through qualifying questions
3. Recommend the best products based on their requirements
4. Handle objections with empathy and provide solutions
5. Create urgency when appropriate (limited stock, deals ending)
6. Guide them toward a purchase decision
7. Schedule appointments when requested
8. Escalate to human agent when needed

CONVERSATION GUIDELINES:
- Be friendly, professional, and helpful
- Ask open-ended questions to understand needs
- Highlight product benefits, not just features
- Use social proof when available
- Address concerns directly and honestly
- Never be pushy or aggressive
- Keep responses concise (2-4 sentences max)
- Use emojis occasionally to be engaging (1-2 per message)

QUALIFYING QUESTIONS TO ASK:
1. What are you looking for today?
2. What's your budget range?
3. When do you need this by?
4. Have you tried similar products before?
5. What's most important to you in this product?

HANDLING OBJECTIONS:
- Price too high → Emphasize value, offer alternatives
- Not sure → Provide social proof, guarantee info
- Need to think → Create gentle urgency, offer to follow up
- Competitor comparison → Highlight unique benefits

CLOSING TECHNIQUES:
- Assume the sale: "Would you like me to help you order this?"
- Create urgency: "This is selling fast, should I reserve one?"
- Offer incentives: "We have free shipping today"
- Simplify: "I can help you complete this in just 2 minutes"

Remember: Your goal is to help the customer find what they need while maximizing sales.
Be genuine, helpful, and always put the customer first."""

    def get_fallback_response(self, language: str = "en") -> str:
        responses = {
            "en": "I apologize for the technical difficulty. Let me connect you with a human agent who can assist you further. Please wait a moment.",
            "es": "Disculpa la dificultad técnica. Déjame conectarte con un agente humano que pueda ayudarte más. Por favor espera un momento.",
            "fr": "Je m'excuse pour la difficulté technique. Laissez-moi vous connecter avec un agent humain qui peut vous aider davantage. Veuillez patienter un moment.",
            "de": "Entschuldigung für die technischen Schwierigkeiten. Lassen Sie mich Sie mit einem menschlichen Agenten verbinden, der Ihnen weiter helfen kann. Bitte warten Sie einen Moment.",
            "tl": "Paumanhin sa teknikal na kahirapan. Hayaan mo akong ikonekta ka sa isang human agent na makakatulong sa iyo. Mangyaring maghintay ng isang sandali."
        }
        return responses.get(language, responses["en"])

    def _format_products(self, products: List[Dict]) -> str:
        if not products:
            return "No products currently available."

        formatted = []
        for product in products:
            features = ", ".join(product.get("features", []))
            formatted.append(
                f"- {product.get('name', 'Unknown')}: ${product.get('price', 0):.2f}\n"
                f"  Description: {product.get('description', 'N/A')}\n"
                f"  Category: {product.get('category', 'N/A')}\n"
                f"  Features: {features}\n"
                f"  In Stock: {'Yes' if product.get('in_stock', True) else 'No'}"
            )

        return "\n\n".join(formatted)

    def _get_language_instructions(self, language: str) -> str:
        instructions = {
            "en": "Respond in English.",
            "es": "Responde en español. The customer prefers Spanish.",
            "fr": "Répondez en français. The customer prefers French.",
            "de": "Antworten Sie auf Deutsch. The customer prefers German.",
            "tl": "Sagutin sa Tagalog. The customer prefers Tagalog.",
            "zh": "用中文回复。The customer prefers Chinese.",
            "ja": "日本語で返信してください。The customer prefers Japanese.",
            "ko": "한국어로 응답해 주세요. The customer prefers Korean.",
        }
        return instructions.get(language, instructions["en"])