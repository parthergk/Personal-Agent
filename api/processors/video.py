import os
import asyncio
import logging
from typing import Optional
from agent import IncomingMessage

logger = logging.getLogger(__name__)

# WhatsApp Cloud API video size limit: 16 MB
MAX_VIDEO_SIZE_MB = 16
MAX_VIDEO_SIZE_BYTES = MAX_VIDEO_SIZE_MB * 1024 * 1024

# Supported video extensions
SUPPORTED_VIDEO_EXTS = {".mp4", ".mov", ".avi", ".mkv", ".3gp", ".webm"}


async def process_video(path: Optional[str], caption: Optional[str], mime_type: Optional[str]) -> IncomingMessage:
    """
    Preprocesses an incoming video message.

    Currently returns the video with a default caption prompting the agent
    to ask the user whether they want to save it. Guards are in place for:
      - Missing file path
      - Non-existent file
      - Unsupported format
      - File too large (> 16 MB)

    Future extension point: add thumbnail extraction or audio transcription
    of the video's audio track here.
    """

    # --- Guard: path must be provided ---
    if not path:
        logger.warning("process_video called with no file path.")
        return IncomingMessage(
            type="video",
            path=path,
            mime_type=mime_type,
            caption="[Video Error]: No file path provided."
        )

    # --- Guard: file must exist ---
    if not os.path.exists(path):
        logger.warning("Video file not found: %s", path)
        return IncomingMessage(
            type="video",
            path=path,
            mime_type=mime_type,
            caption="[Video Error]: File not found."
        )

    # --- Guard: file size ---
    try:
        file_size = os.path.getsize(path)
    except OSError as e:
        logger.error("Could not read video file size for %s: %s", path, e)
        return IncomingMessage(
            type="video",
            path=path,
            mime_type=mime_type,
            caption=f"[Video Error]: Could not access file — {e}"
        )

    if file_size > MAX_VIDEO_SIZE_BYTES:
        size_mb = file_size / (1024 * 1024)
        logger.warning("Video file too large: %.1f MB (limit %d MB)", size_mb, MAX_VIDEO_SIZE_MB)
        return IncomingMessage(
            type="video",
            path=path,
            mime_type=mime_type,
            caption=(
                f"[Video Error]: File is too large ({size_mb:.1f} MB). "
                f"Maximum allowed is {MAX_VIDEO_SIZE_MB} MB."
            )
        )

    # --- Guard: unsupported format ---
    ext = os.path.splitext(path)[1].lower()
    mime = (mime_type or "").lower()
    if not mime.startswith("video/") and ext not in SUPPORTED_VIDEO_EXTS:
        logger.warning("Unsupported video format: ext=%s mime=%s path=%s", ext, mime, path)
        return IncomingMessage(
            type="video",
            path=path,
            mime_type=mime_type,
            caption=f"[Video Error]: Unsupported video format ({ext or mime or 'unknown'})."
        )

    # All checks passed — return with default caption for the agent to handle
    size_mb = file_size / (1024 * 1024)
    logger.info("Video processed: %s (%.1f MB)", path, size_mb)
    return IncomingMessage(
        type="video",
        path=path,
        mime_type=mime_type,
        caption=caption or "You uploaded a video. Do you want to save it?"
    )
