from datetime import datetime
from typing import Dict, Optional, List
from loguru import logger

from app.models.schemas import (
    Conversation, ConversationState, ConversationMessage,
    Lead, LeadStatus, MessageStatus, Product
)
from app.ai.engine import AIEngine
from app.ai.language import LanguageDetector
from app.services.products import ProductService
from app.services.handoff import HandoffService
from app.services.scheduler import SchedulerService
from app.config import settings


class ConversationService:
    def __init__(self):
        self.conversations: Dict[str, Conversation] = {}
        self.ai_engine = AIEngine()
        self.product_service = ProductService()
        self.handoff_service = HandoffService()
        self.scheduler_service = SchedulerService()
        self.stats = {
            "total_conversations": 0,
            "active_conversations": 0,
            "leads_generated": 0,
            "appointments_scheduled": 0,
            "handoffs": 0
        }

    async def handle_message(self, sender_id: str, text: str) -> str:
        conversation = self._get_or_create_conversation(sender_id)

        if conversation.status == MessageStatus.HANDOFF:
            return await self._handle_handoff_message(conversation, text)

        if self._is_handoff_request(text):
            return await self._initiate_handoff(conversation)

        if self._is_scheduling_request(text):
            return await self._handle_scheduling(conversation, text)

        detected_language = LanguageDetector.detect_simple(text)
        if detected_language != conversation.language:
            conversation.language = detected_language

        conversation.messages.append(
            ConversationMessage(role="user", content=text)
        )

        products = await self.product_service.get_products()
        products_dicts = [p.dict() for p in products] if hasattr(products[0], 'dict') else products

        response = await self.ai_engine.generate_response(
            user_message=text,
            conversation_history=[{"role": m.role, "content": m.content} for m in conversation.messages],
            products=products_dicts,
            language=conversation.language
        )

        conversation.messages.append(
            ConversationMessage(role="assistant", content=response)
        )

        self._update_conversation_state(conversation, text)

        if conversation.state == ConversationState.QUALIFYING:
            await self._extract_lead_info(conversation, text)

        return response

    async def handle_postback(self, sender_id: str, payload: str) -> str:
        conversation = self._get_or_create_conversation(sender_id)

        if payload.startswith("VIEW_PRODUCT_"):
            product_id = payload.replace("VIEW_PRODUCT_", "")
            product = await self.product_service.get_product_by_id(product_id)
            if product:
                return self._format_product_details(product)

        elif payload.startswith("ADD_CART_"):
            product_id = payload.replace("ADD_CART_", "")
            product = await self.product_service.get_product_by_id(product_id)
            if product:
                return f"Great choice! I've added {product.name} to your cart. Would you like to continue shopping or proceed to checkout?"

        elif payload == "GET_STARTED":
            return await self._handle_greeting(conversation)

        elif payload == "HUMAN_AGENT":
            return await self._initiate_handoff(conversation)

        return "I'm not sure how to handle that. How can I help you?"

    async def _handle_greeting(self, conversation: Conversation) -> str:
        conversation.state = ConversationState.GREETING

        greeting = f"Welcome to {settings.business_name}! 🎉\n\n"
        greeting += "I'm your personal shopping assistant. I can help you:\n"
        greeting += "• Find the perfect product\n"
        greeting += "• Get recommendations based on your needs\n"
        greeting += "• Answer any questions you have\n"
        greeting += "• Schedule an appointment\n\n"
        greeting += "What are you looking for today?"

        conversation.messages.append(
            ConversationMessage(role="assistant", content=greeting)
        )

        return greeting

    async def _handle_handoff_message(self, conversation: Conversation, text: str) -> str:
        logger.info(f"Handoff message from {conversation.messenger_id}: {text}")
        return "Your message has been forwarded to our support team. A human agent will respond shortly. Please wait..."

    async def _handle_scheduling(self, conversation: Conversation, text: str) -> str:
        conversation.state = ConversationState.SCHEDULING

        available_slots = await self.scheduler_service.get_available_slots()

        if available_slots:
            slots_text = "\n".join([
                f"• {slot['date']} at {slot['time']}"
                for slot in available_slots[:5]
            ])
            return f"Here are the available appointment slots:\n\n{slots_text}\n\nWhich slot works best for you?"
        else:
            return "I'd be happy to help you schedule an appointment. Please let me know your preferred date and time, and I'll check availability."

    def _is_handoff_request(self, text: str) -> bool:
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in settings.human_handoff_keywords)

    def _is_scheduling_request(self, text: str) -> bool:
        scheduling_keywords = ["schedule", "appointment", "book", "meeting", "call", "demo"]
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in scheduling_keywords)

    async def _initiate_handoff(self, conversation: Conversation) -> str:
        conversation.state = ConversationState.HANDOFF
        conversation.status = MessageStatus.HANDOFF
        self.stats["handoffs"] += 1

        await self.handoff_service.notify_human_agent(conversation)

        return "I'll connect you with a human agent who can better assist you. Please wait a moment while I transfer you. 🙋"

    def _get_or_create_conversation(self, sender_id: str) -> Conversation:
        if sender_id not in self.conversations:
            self.conversations[sender_id] = Conversation(
                messenger_id=sender_id,
                state=ConversationState.GREETING
            )
            self.stats["total_conversations"] += 1
            self.stats["active_conversations"] += 1

        return self.conversations[sender_id]

    def _update_conversation_state(self, conversation: Conversation, text: str):
        text_lower = text.lower()

        if conversation.state == ConversationState.GREETING:
            if any(word in text_lower for word in ["looking for", "need", "want", "buy", "shop"]):
                conversation.state = ConversationState.QUALIFYING

        elif conversation.state == ConversationState.QUALIFYING:
            if any(word in text_lower for word in ["recommend", "suggest", "which", "best"]):
                conversation.state = ConversationState.RECOMMENDING

        elif conversation.state == ConversationState.RECOMMENDING:
            if any(word in text_lower for word in ["price", "cost", "expensive", "cheap", "discount"]):
                conversation.state = ConversationState.HANDLING_OBJECTIONS

        elif conversation.state == ConversationState.HANDLING_OBJECTIONS:
            if any(word in text_lower for word in ["okay", "deal", "buy", "order", "yes"]):
                conversation.state = ConversationState.CLOSING

        conversation.updated_at = datetime.utcnow()

    async def _extract_lead_info(self, conversation: Conversation, text: str):
        text_lower = text.lower()

        if not conversation.lead:
            conversation.lead = Lead(
                id=conversation.messenger_id,
                messenger_id=conversation.messenger_id
            )
            self.stats["leads_generated"] += 1

        if "@" in text:
            conversation.lead.email = text
        elif any(char.isdigit() for char in text) and len(text) >= 10:
            conversation.lead.phone = text

        conversation.lead.notes.append(text)
        conversation.lead.updated_at = datetime.utcnow()

    def _format_product_details(self, product: Product) -> str:
        features = "\n".join([f"• {f}" for f in product.features]) if product.features else "No features listed"

        return f"""📦 {product.name}

{product.description}

💰 Price: ${product.price:.2f}
📂 Category: {product.category}
✅ In Stock: {'Yes' if product.in_stock else 'No'}

✨ Features:
{features}

Would you like to add this to your cart?"""

    def get_stats(self) -> Dict:
        return self.stats