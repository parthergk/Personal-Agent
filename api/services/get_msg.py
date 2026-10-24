import os
import time
import logging
import mimetypes
import httpx
from typing import Optional
from agent.models import IncomingMessage

logger = logging.getLogger(__name__)

GRAPH_API_VERSION = "v21.0"
BASE_GRAPH_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}"

# Common MIME type to file extension mapping
MIME_TO_EXTENSION = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
    "audio/ogg; codecs=opus": ".ogg",
    "audio/ogg": ".ogg",
    "audio/mpeg": ".mp3",
    "audio/mp4": ".m4a",
    "audio/aac": ".aac",
    "audio/wav": ".wav",
    "video/mp4": ".mp4",
    "video/3gpp": ".3gp",
    "video/quicktime": ".mov",
    "application/pdf": ".pdf",
    "text/plain": ".txt",
}


async def save_media(
    media_id: str,
    mime_type: Optional[str] = None,
    original_filename: Optional[str] = None,
) -> str:
    """
    Downloads media from WhatsApp Cloud API and saves it to the local uploads directory.
    Equivalent to saveMedia.ts in the Baileys implementation.
    """
    whatsapp_token = os.getenv("WHATSAPP_TOKEN")
    if not whatsapp_token:
        raise ValueError("WHATSAPP_TOKEN environment variable is not configured.")

    headers = {"Authorization": f"Bearer {whatsapp_token}"}

    async with httpx.AsyncClient(timeout=30.0) as client:
        # Step 1: Retrieve the media download URL from Graph API
        media_res = await client.get(f"{BASE_GRAPH_URL}/{media_id}", headers=headers)
        media_res.raise_for_status()
        media_data = media_res.json()

        download_url = media_data.get("url")
        if not download_url:
            raise ValueError(f"No download URL returned by Meta for media ID: {media_id}")
        detected_mime = media_data.get("mime_type") or mime_type

        # Step 2: Download raw binary data from lookaside URL
        dl_headers = {
            "Authorization": f"Bearer {whatsapp_token}",
            "User-Agent": "curl/7.64.1",
        }
        file_res = await client.get(download_url, headers=dl_headers)
        file_res.raise_for_status()
        content = file_res.content

    # Step 3: Determine appropriate file extension
    ext = None
    if original_filename and "." in original_filename:
        ext = os.path.splitext(original_filename)[1]
    if not ext and detected_mime:
        clean_mime = detected_mime.split(";")[0].strip().lower()
        ext = (
            MIME_TO_EXTENSION.get(detected_mime)
            or MIME_TO_EXTENSION.get(clean_mime)
            or mimetypes.guess_extension(clean_mime)
        )
    if not ext:
        ext = ".bin"

    uploads_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "uploads"))
    os.makedirs(uploads_dir, exist_ok=True)

    filename = f"{int(time.time() * 1000)}_{media_id}{ext}"
    filepath = os.path.join(uploads_dir, filename)

    with open(filepath, "wb") as f:
        f.write(content)

    logger.info(f"Saved incoming WhatsApp media to {filepath}")
    return filepath


async def get_msg(raw_message: dict) -> Optional[IncomingMessage]:
    """
    Parses a raw WhatsApp Webhook message object and converts it to IncomingMessage.
    Equivalent to getMsg.ts in the Baileys implementation.
    """
    msg_type = raw_message.get("type")
    if not msg_type:
        return None

    if msg_type == "text":
        body = raw_message.get("text", {}).get("body", "")
        return IncomingMessage(
            type="text",
            caption=body,
        )

    elif msg_type == "image":
        img = raw_message.get("image", {})
        media_id = img.get("id")
        mime_type = img.get("mime_type", "image/jpeg")
        caption = img.get("caption") or ""

        file_path = None
        if media_id:
            try:
                file_path = await save_media(media_id, mime_type=mime_type)
            except Exception as e:
                logger.error(f"Error saving WhatsApp image media {media_id}: {e}")

        return IncomingMessage(
            type="image",
            path=file_path,
            caption=caption,
            mime_type=mime_type,
        )

    elif msg_type in ("audio", "voice"):
        audio = raw_message.get(msg_type, {})
        media_id = audio.get("id")
        mime_type = audio.get("mime_type", "audio/ogg; codecs=opus")

        file_path = None
        if media_id:
            try:
                file_path = await save_media(media_id, mime_type=mime_type)
            except Exception as e:
                logger.error(f"Error saving WhatsApp audio media {media_id}: {e}")

        return IncomingMessage(
            type="audio",
            path=file_path,
            mime_type=mime_type,
        )

    elif msg_type == "video":
        video = raw_message.get("video", {})
        media_id = video.get("id")
        mime_type = video.get("mime_type", "video/mp4")
        caption = video.get("caption") or ""

        file_path = None
        if media_id:
            try:
                file_path = await save_media(media_id, mime_type=mime_type)
            except Exception as e:
                logger.error(f"Error saving WhatsApp video media {media_id}: {e}")

        return IncomingMessage(
            type="video",
            path=file_path,
            caption=caption,
            mime_type=mime_type,
        )

    elif msg_type == "document":
        doc = raw_message.get("document", {})
        media_id = doc.get("id")
        mime_type = doc.get("mime_type", "application/octet-stream")
        filename = doc.get("filename")
        caption = doc.get("caption") or ""

        file_path = None
        if media_id:
            try:
                file_path = await save_media(
                    media_id, mime_type=mime_type, original_filename=filename
                )
            except Exception as e:
                logger.error(f"Error saving WhatsApp document media {media_id}: {e}")

        return IncomingMessage(
            type="document",
            path=file_path,
            caption=caption,
            mime_type=mime_type,
        )

    return None
