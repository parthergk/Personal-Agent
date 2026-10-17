import os
import logging
import httpx

logger = logging.getLogger(__name__)

GRAPH_API_VERSION = "v21.0"
BASE_GRAPH_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}"


async def send_whatsapp_message(to: str, message: str) -> dict:
    """
    Sends a text message reply to a WhatsApp user using Cloud API.
    """
    whatsapp_token = os.getenv("WHATSAPP_TOKEN")
    phone_number_id = os.getenv("PHONE_NUMBER_ID")

    if not whatsapp_token or not phone_number_id:
        logger.error("Missing WHATSAPP_TOKEN or PHONE_NUMBER_ID in environment.")
        return {}

    url = f"{BASE_GRAPH_URL}/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {whatsapp_token}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "text",
        "text": {"body": message},
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        res = await client.post(url, json=payload, headers=headers)
        if res.is_error:
            logger.error("WhatsApp API error: %s", res.text)
        res.raise_for_status()
        return res.json()
