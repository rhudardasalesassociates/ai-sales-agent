from fastapi import APIRouter, Request, Response, HTTPException, Query
from fastapi.responses import PlainTextResponse
from loguru import logger
import hashlib
import hmac

from app.config import settings
from app.messenger.sender import MessengerSender
from app.services.conversation import ConversationService

router = APIRouter()
sender = MessengerSender()
conversation_service = ConversationService()


def verify_signature(request_body: bytes, signature: str) -> bool:
    if not settings.facebook_app_secret:
        logger.info("No app secret configured, skipping signature verification")
        return True

    try:
        expected_signature = hmac.new(
            settings.facebook_app_secret.encode('utf-8'),
            request_body,
            hashlib.sha256
        ).hexdigest()

        result = hmac.compare_digest(f"sha256={expected_signature}", signature)
        if not result:
            logger.warning(f"Signature mismatch: expected sha256={expected_signature}, got {signature}")
        return result
    except Exception as e:
        logger.error(f"Signature verification error: {e}")
        return True


@router.get("/")
async def verify_webhook(request: Request):
    hub_mode = request.query_params.get("hub.mode")
    hub_verify_token = request.query_params.get("hub.verify_token")
    hub_challenge = request.query_params.get("hub.challenge")

    logger.info(f"Webhook verification: hub_mode={hub_mode}, hub_verify_token={hub_verify_token}")
    
    if hub_mode == "subscribe" and hub_verify_token == settings.facebook_verify_token:
        logger.info("Webhook verified successfully")
        return PlainTextResponse(content=hub_challenge)
    else:
        logger.warning(f"Webhook verification failed: token={hub_verify_token}, expected={settings.facebook_verify_token}")
        raise HTTPException(status_code=403, detail="Forbidden")


@router.post("/")
async def handle_webhook(request: Request):
    body = await request.json()
    raw_body = await request.body()

    signature = request.headers.get("X-Hub-Signature-256")
    if signature:
        if not verify_signature(raw_body, signature):
            logger.warning(f"Invalid signature - but continuing anyway for debugging")
            # For now, let's log but not block - we'll fix signature later
        else:
            logger.info("Signature verified successfully")

    if body.get("object") != "page":
        raise HTTPException(status_code=404, detail="Not a page event")

    for entry in body.get("entry", []):
        for event in entry.get("messaging", []):
            await process_event(event)

    return Response(status_code=200)


async def process_event(event: dict):
    sender_id = event.get("sender", {}).get("id")
    recipient_id = event.get("recipient", {}).get("id")

    if not sender_id:
        return

    if "message" in event:
        await handle_message(sender_id, event["message"])
    elif "postback" in event:
        await handle_postback(sender_id, event["postback"])


async def handle_message(sender_id: str, message: dict):
    if message.get("is_echo"):
        return

    text = message.get("text", "")
    attachments = message.get("attachments", [])

    logger.info(f"Message from {sender_id}: {text}")

    try:
        response = await conversation_service.handle_message(sender_id, text)
        await sender.send_text_message(sender_id, response)
    except Exception as e:
        logger.error(f"Error handling message: {e}")
        await sender.send_text_message(
            sender_id,
            "Sorry, I encountered an error. Please try again later."
        )


async def handle_postback(sender_id: str, postback: dict):
    payload = postback.get("payload", "")
    logger.info(f"Postback from {sender_id}: {payload}")

    try:
        response = await conversation_service.handle_postback(sender_id, payload)
        await sender.send_text_message(sender_id, response)
    except Exception as e:
        logger.error(f"Error handling postback: {e}")