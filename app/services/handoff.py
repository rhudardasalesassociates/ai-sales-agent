from datetime import datetime, timedelta
from typing import Dict, List, Optional
from loguru import logger

from app.models.schemas import Conversation


class HandoffService:
    def __init__(self):
        self.pending_handoffs: List[Dict] = []
        self.agents: List[Dict] = []

    async def notify_human_agent(self, conversation: Conversation) -> bool:
        handoff_request = {
            "conversation_id": conversation.messenger_id,
            "timestamp": datetime.utcnow().isoformat(),
            "language": conversation.language,
            "message_count": len(conversation.messages),
            "last_messages": [
                {"role": m.role, "content": m.content}
                for m in conversation.messages[-5:]
            ],
            "lead_info": conversation.lead.dict() if conversation.lead else None,
            "status": "pending"
        }

        self.pending_handoffs.append(handoff_request)

        logger.info(f"Handoff requested for conversation {conversation.messenger_id}")

        await self._send_notification_to_agents(handoff_request)

        return True

    async def _send_notification_to_agents(self, handoff_request: Dict) -> None:
        logger.info(f"Notification sent to agents for conversation {handoff_request['conversation_id']}")

    async def assign_agent(self, conversation_id: str, agent_id: str) -> bool:
        for handoff in self.pending_handoffs:
            if handoff["conversation_id"] == conversation_id:
                handoff["agent_id"] = agent_id
                handoff["status"] = "assigned"
                handoff["assigned_at"] = datetime.utcnow().isoformat()
                return True
        return False

    async def complete_handoff(self, conversation_id: str) -> bool:
        for i, handoff in enumerate(self.pending_handoffs):
            if handoff["conversation_id"] == conversation_id:
                self.pending_handoffs[i]["status"] = "completed"
                self.pending_handoffs[i]["completed_at"] = datetime.utcnow().isoformat()
                return True
        return False

    def get_pending_handoffs(self) -> List[Dict]:
        return [h for h in self.pending_handoffs if h["status"] == "pending"]

    def get_handoff_stats(self) -> Dict:
        total = len(self.pending_handoffs)
        pending = len([h for h in self.pending_handoffs if h["status"] == "pending"])
        assigned = len([h for h in self.pending_handoffs if h["status"] == "assigned"])
        completed = len([h for h in self.pending_handoffs if h["status"] == "completed"])

        return {
            "total": total,
            "pending": pending,
            "assigned": assigned,
            "completed": completed
        }