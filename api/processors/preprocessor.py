from agent import IncomingMessage
from .image import process_image
from .audio import process_audio
from .video import process_video
from .document import process_document
import re

async def preprocess_message(message: IncomingMessage) -> IncomingMessage:
    if message.type == "text":
        url_match = re.search(r'https?://[^\s]+', message.caption or "")
        file_path = url_match.group(0).rstrip(".,!?;:)]}") if url_match else None
        
        return IncomingMessage(
            type="link" if file_path else "text",
            file_path=file_path,
            caption=message.caption
        )
    elif message.type == "image":
        return await process_image(message.path, message.caption, message.mime_type)
    elif message.type == "audio":
        return await process_audio(message.path, message.mime_type)
    elif message.type == "video":
        return await process_video(message.path, message.caption, message.mime_type)
    elif message.type == "document":
        return await process_document(message.path, message.caption, message.mime_type)
    return message
