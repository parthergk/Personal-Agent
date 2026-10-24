import os
import logging
from typing import Optional
from agent import IncomingMessage

# Import other processors for routing when a media file is sent as a document
from .image import process_image
from .audio import process_audio
from .video import process_video

logger = logging.getLogger(__name__)

# Max size for inline text-document reading (prevent huge files flooding the LLM context)
MAX_TEXT_DOC_SIZE_BYTES = 100 * 1024  # 100 KB


async def process_document(path: Optional[str], caption: Optional[str], mime_type: Optional[str]) -> IncomingMessage:
    if not path:
        return IncomingMessage(
            type="document",
            path=path,
            caption="[Document Error]: No file path provided. Please ask the user to re-send the document.",
            mime_type=mime_type
        )

    # 1. Determine type by MIME-type and file extension
    ext = os.path.splitext(path)[1].lower()
    mime = mime_type.lower() if mime_type else ""

    # --- Guard: file must exist before routing ---
    if not os.path.exists(path):
        filename = os.path.basename(path)
        logger.warning("Document file not found: %s", path)
        return IncomingMessage(
            type="document",
            path=path,
            caption=f"[Document Error]: The document ({filename}) could not be loaded or was corrupted. Please ask the user to re-send the file.",
            mime_type=mime_type
        )

    # 2. Route to image processor if it's actually an image
    if mime.startswith("image/") or ext in {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tiff"}:
        return await process_image(path, caption, mime_type)

    # 3. Route to audio processor if it's actually an audio file
    elif mime.startswith("audio/") or ext in {".mp3", ".ogg", ".wav", ".m4a", ".aac", ".amr", ".opus"}:
        return await process_audio(path, mime_type)

    # 4. Route to video processor if it's actually a video
    elif mime.startswith("video/") or ext in {".mp4", ".mov", ".avi", ".mkv", ".3gp", ".webm"}:
        return await process_video(path, caption, mime_type)

    # 5. Handle text-based documents — read and inject content inline
    elif ext in {".txt", ".md", ".json", ".xml", ".csv", ".ini", ".yaml", ".yml", ".py", ".js", ".ts", ".html", ".css"}:
        try:
            file_size = os.path.getsize(path)
            filename = os.path.basename(path)

            if file_size > MAX_TEXT_DOC_SIZE_BYTES:
                size_kb = file_size / 1024
                logger.warning("Text document too large to inline: %.1f KB (%s)", size_kb, path)
                return IncomingMessage(
                    type="document",
                    path=path,
                    caption=caption or (
                        f"[Document Error]: The document ({filename}) is too large to read inline "
                        f"({size_kb:.0f} KB, limit is {MAX_TEXT_DOC_SIZE_BYTES // 1024} KB). Ask the user if they want to save it as a file."
                    ),
                    mime_type=mime_type
                )

            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content_text = f.read()

            return IncomingMessage(
                type="document",
                path=path,
                caption=caption or (
                    f"Here is the content of the document ({filename}):\n"
                    f"<document name=\"{filename}\">\n{content_text}\n</document>"
                ),
                mime_type=mime_type
            )
        except OSError as e:
            logger.error("Failed to read text document %s: %s", path, e)
            return IncomingMessage(
                type="document",
                path=path,
                caption="[Document Error]: Unable to read the text document due to a file error. Please ask the user to re-send the document.",
                mime_type=mime_type
            )

    # 6. Stub routing for Office files and Archives
    elif ext == ".pdf":
        return IncomingMessage(
            type="document",
            path=path,
            caption=caption or "Ask the user. You uploaded a PDF document. Do you want to save it?",
            mime_type=mime_type
        )
    elif ext in {".docx", ".doc"}:
        return IncomingMessage(
            type="document",
            path=path,
            caption=caption or "Ask the user. You uploaded a Word document. Do you want to save it?",
            mime_type=mime_type
        )
    elif ext in {".xlsx", ".xls"}:
        return IncomingMessage(
            type="document",
            path=path,
            caption=caption or "Ask the user. You uploaded an Excel spreadsheet. Do you want to save it?",
            mime_type=mime_type
        )
    elif ext in {".zip", ".rar", ".tar", ".gz"}:
        return IncomingMessage(
            type="document",
            path=path,
            caption=caption or "Ask the user. You uploaded an archive file. Do you want to save it?",
            mime_type=mime_type
        )

    # 7. Fallback for unsupported binary formats
    filename = os.path.basename(path)
    return IncomingMessage(
        type="document",
        path=path,
        caption=caption or f"Ask the user. You uploaded a document ({filename}). Do you want to save it?",
        mime_type=mime_type
    )
