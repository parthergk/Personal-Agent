import os
import logging
import mimetypes
from typing import Optional
import httpx

logger = logging.getLogger(__name__)

GRAPH_API_VERSION = "v21.0"
BASE_GRAPH_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}"

# Common file extension to MIME type mapping supported by WhatsApp Cloud API
MIME_MAP = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
    ".gif": "image/gif",
    ".mp4": "video/mp4",
    ".3gp": "video/3gpp",
    ".mov": "video/quicktime",
    ".mp3": "audio/mpeg",
    ".ogg": "audio/ogg",
    ".m4a": "audio/mp4",
    ".aac": "audio/aac",
    ".wav": "audio/wav",
    ".pdf": "application/pdf",
    ".txt": "text/plain",
    ".doc": "application/msword",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".xls": "application/vnd.ms-excel",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}


def _resolve_file_path(file_path: str) -> str:
    """
    Resolves relative or absolute file paths against current directory and api root.
    """
    if os.path.isabs(file_path) and os.path.exists(file_path):
        return file_path

    abs_path = os.path.abspath(file_path)
    if os.path.exists(abs_path):
        return abs_path

    api_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    candidate = os.path.join(api_root, file_path)
    if os.path.exists(candidate):
        return candidate

    return abs_path


async def upload_media(file_path: str, mime_type: Optional[str] = None) -> str:
    """
    Uploads a local media file to WhatsApp Cloud API and returns the media_id.
    Endpoint: POST /{phone_number_id}/media
    """
    resolved_path = _resolve_file_path(file_path)
    if not os.path.exists(resolved_path):
        raise FileNotFoundError(f"Media file not found: {resolved_path}")

    whatsapp_token = os.getenv("WHATSAPP_TOKEN")
    phone_number_id = os.getenv("PHONE_NUMBER_ID")

    if not whatsapp_token or not phone_number_id:
        raise ValueError("Missing WHATSAPP_TOKEN or PHONE_NUMBER_ID in environment.")

    # Determine MIME type
    if not mime_type:
        ext = os.path.splitext(resolved_path)[1].lower()
        mime_type = MIME_MAP.get(ext) or mimetypes.guess_type(resolved_path)[0] or "application/octet-stream"

    filename = os.path.basename(resolved_path)
    url = f"{BASE_GRAPH_URL}/{phone_number_id}/media"
    headers = {
        "Authorization": f"Bearer {whatsapp_token}",
    }

    with open(resolved_path, "rb") as f:
        file_bytes = f.read()

    files = {
        "file": (filename, file_bytes, mime_type),
    }
    data = {
        "messaging_product": "whatsapp",
        "type": mime_type,
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        res = await client.post(url, headers=headers, data=data, files=files)
        if res.is_error:
            logger.error("WhatsApp Media Upload API error: %s", res.text)
        res.raise_for_status()
        result = res.json()
        media_id = result.get("id")
        if not media_id:
            raise ValueError(f"No media ID returned by Meta: {result}")
        return media_id


async def send_whatsapp_message(
    to: str,
    message: str = "",
    type: str = "text",
    path: Optional[str] = None,
) -> dict:
    """
    Sends a WhatsApp message (text or media) using Meta Cloud API.
    If path is provided and exists, uploads the media and sends it with message as caption.
    """
    whatsapp_token = os.getenv("WHATSAPP_TOKEN")
    phone_number_id = os.getenv("PHONE_NUMBER_ID")

    if not whatsapp_token or not phone_number_id:
        logger.error("Missing WHATSAPP_TOKEN or PHONE_NUMBER_ID in environment.")
        return {}

    # Check and resolve path if media is provided
    resolved_path = _resolve_file_path(path) if path else None

    # Auto-detect media type if path is valid but type was left as default
    if resolved_path and os.path.exists(resolved_path):
        if type == "text":
            ext = os.path.splitext(resolved_path)[1].lower()
            if ext in (".jpg", ".jpeg", ".png", ".webp", ".gif"):
                type = "image"
            elif ext in (".mp4", ".3gp", ".mov"):
                type = "video"
            elif ext in (".mp3", ".ogg", ".wav", ".m4a", ".aac"):
                type = "audio"
            else:
                type = "document"

    # Send media message if path exists and type is a supported media type
    if resolved_path and os.path.exists(resolved_path) and type in ("image", "video", "document", "audio"):
        try:
            media_id = await upload_media(resolved_path)
            logger.info("Uploaded WhatsApp media %s -> media_id: %s", resolved_path, media_id)

            url = f"{BASE_GRAPH_URL}/{phone_number_id}/messages"
            headers = {
                "Authorization": f"Bearer {whatsapp_token}",
                "Content-Type": "application/json",
            }

            media_payload = {"id": media_id}
            if message and type in ("image", "video", "document"):
                media_payload["caption"] = message

            if type == "document":
                media_payload["filename"] = os.path.basename(resolved_path)

            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": to,
                "type": type,
                type: media_payload,
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                res = await client.post(url, json=payload, headers=headers)
                if res.is_error:
                    logger.error("WhatsApp Send Media API error: %s", res.text)
                res.raise_for_status()
                result = res.json()

            # For audio, Meta Cloud API does not accept captions inside audio object,
            # so send caption as a follow-up text message if present.
            if type == "audio" and message:
                await send_whatsapp_message(to=to, message=message, type="text")

            return result

        except Exception as e:
            logger.error("Failed to send WhatsApp media (%s): %s. Falling back to text.", resolved_path, e)
            if message:
                return await send_whatsapp_message(to=to, message=message, type="text")
            return {}

    # Standard text message
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
        "text": {"body": message or ""},
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        res = await client.post(url, json=payload, headers=headers)
        if res.is_error:
            logger.error("WhatsApp API error: %s", res.text)
        res.raise_for_status()
        return res.json()


async def mark_as_read_and_typing(message_id: str) -> bool:
    """
    Marks the user's incoming message as read (blue ticks)
    and starts the 'typing...' indicator on WhatsApp.
    Endpoint: POST /{phone_number_id}/messages
    """
    whatsapp_token = os.getenv("WHATSAPP_TOKEN")
    phone_number_id = os.getenv("PHONE_NUMBER_ID")

    if not whatsapp_token or not phone_number_id:
        logger.warning("Missing WHATSAPP_TOKEN or PHONE_NUMBER_ID; cannot mark message as read.")
        return False

    url = f"{BASE_GRAPH_URL}/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {whatsapp_token}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "status": "read",
        "message_id": message_id,
        "typing_indicator": {
            "type": "text"
        }
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.post(url, headers=headers, json=payload)
            if res.status_code == 400:
                # Fallback to standard mark-as-read if typing_indicator is rejected
                fallback_payload = {
                    "messaging_product": "whatsapp",
                    "status": "read",
                    "message_id": message_id,
                }
                res = await client.post(url, headers=headers, json=fallback_payload)
            res.raise_for_status()
            logger.info("Marked message %s as read and started typing indicator.", message_id)
            return True
    except Exception as e:
        logger.warning("Failed to mark message %s as read/typing: %s", message_id, e)
        return False

