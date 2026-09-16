import httpx
from loguru import logger
from typing import Optional, List, Dict, Any

from app.config import settings


class MessengerSender:
    def __init__(self):
        self.api_url = "https://graph.facebook.com/v18.0/me/messages"
        self.access_token = settings.facebook_page_access_token

    async def send_text_message(self, recipient_id: str, text: str) -> bool:
        payload = {
            "recipient": {"id": recipient_id},
            "message": {"text": text}
        }
        return await self._send_message(payload)

    async def send_quick_replies(
        self,
        recipient_id: str,
        text: str,
        quick_replies: List[Dict[str, str]]
    ) -> bool:
        payload = {
            "recipient": {"id": recipient_id},
            "message": {
                "text": text,
                "quick_replies": quick_replies
            }
        }
        return await self._send_message(payload)

    async def send_button_template(
        self,
        recipient_id: str,
        text: str,
        buttons: List[Dict[str, Any]]
    ) -> bool:
        payload = {
            "recipient": {"id": recipient_id},
            "message": {
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "button",
                        "text": text,
                        "buttons": buttons
                    }
                }
            }
        }
        return await self._send_message(payload)

    async def send_generic_template(
        self,
        recipient_id: str,
        elements: List[Dict[str, Any]]
    ) -> bool:
        payload = {
            "recipient": {"id": recipient_id},
            "message": {
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "generic",
                        "elements": elements
                    }
                }
            }
        }
        return await self._send_message(payload)

    async def send_product_carousel(
        self,
        recipient_id: str,
        products: List[Dict[str, Any]]
    ) -> bool:
        elements = []
        for product in products[:10]:
            element = {
                "title": product.get("name", "Product"),
                "image_url": product.get("image_url", ""),
                "subtitle": f"${product.get('price', 0):.2f}",
                "buttons": [
                    {
                        "type": "postback",
                        "title": "View Details",
                        "payload": f"VIEW_PRODUCT_{product.get('id', '')}"
                    },
                    {
                        "type": "postback",
                        "title": "Add to Cart",
                        "payload": f"ADD_CART_{product.get('id', '')}"
                    }
                ]
            }
            elements.append(element)

        return await self.send_generic_template(recipient_id, elements)

    async def send_typing_on(self, recipient_id: str) -> bool:
        payload = {
            "recipient": {"id": recipient_id},
            "sender_action": "typing_on"
        }
        return await self._send_message(payload)

    async def send_typing_off(self, recipient_id: str) -> bool:
        payload = {
            "recipient": {"id": recipient_id},
            "sender_action": "typing_off"
        }
        return await self._send_message(payload)

    async def _send_message(self, payload: Dict[str, Any]) -> bool:
        params = {"access_token": self.access_token}

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.api_url,
                    json=payload,
                    params=params,
                    timeout=10.0
                )

                if response.status_code == 200:
                    return True
                else:
                    logger.error(
                        f"Failed to send message: {response.status_code} - "
                        f"{response.text}"
                    )
                    return False

            except Exception as e:
                logger.error(f"Error sending message: {e}")
                return False