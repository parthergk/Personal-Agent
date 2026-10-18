import os
import asyncio
import logging
from dotenv import load_dotenv
from sarvamai import AsyncSarvamAI
from sarvamai.core.api_error import ApiError
from typing import Optional
from agent import IncomingMessage

load_dotenv()

logger = logging.getLogger(__name__)

api_key = os.getenv("SARVAM_API_KEY")
if not api_key:
    raise RuntimeError("SARVAM_API_KEY is not configured")

sarvam_client = AsyncSarvamAI(api_subscription_key=api_key)

# Sarvam STT limits: max 25 MB per request
MAX_AUDIO_SIZE_MB = 25
MAX_AUDIO_SIZE_BYTES = MAX_AUDIO_SIZE_MB * 1024 * 1024

# Timeout for the transcription API call (seconds)
TRANSCRIBE_TIMEOUT_SECONDS = 60

# Number of retries on transient server errors (5xx)
MAX_RETRIES = 2
RETRY_DELAY_SECONDS = 2


async def process_audio(path, mime_type: Optional[str]) -> IncomingMessage:
    # --- Guard: file must exist ---
    if not path or not os.path.exists(path):
        logger.warning("Audio file not found: %s", path)
        return IncomingMessage(
            type="audio",
            path=path,
            mime_type=mime_type,
            caption="[Audio Error]: File not found."
        )

    # --- Guard: file size ---
    file_size = os.path.getsize(path)
    if file_size > MAX_AUDIO_SIZE_BYTES:
        size_mb = file_size / (1024 * 1024)
        logger.warning("Audio file too large: %.1f MB (limit %d MB)", size_mb, MAX_AUDIO_SIZE_MB)
        return IncomingMessage(
            type="audio",
            path=path,
            mime_type=mime_type,
            caption=f"[Audio Error]: File is too large ({size_mb:.1f} MB). Maximum allowed is {MAX_AUDIO_SIZE_MB} MB."
        )

    last_error: Exception | None = None

    for attempt in range(1, MAX_RETRIES + 2):  # attempts: 1, 2, 3
        try:
            with open(path, "rb") as audio_file:
                response = await asyncio.wait_for(
                    sarvam_client.speech_to_text.transcribe(
                        file=audio_file,
                        model="saaras:v3",
                        mode="translit",
                        language_code="unknown",
                    ),
                    timeout=TRANSCRIBE_TIMEOUT_SECONDS
                )

            transcript = (response.transcript or "").strip()
            if not transcript:
                logger.warning("Sarvam returned an empty transcript for: %s", path)
                return IncomingMessage(
                    type="audio",
                    path=path,
                    mime_type=mime_type,
                    caption="[Audio Transcript]: (No speech detected)"
                )

            return IncomingMessage(
                type="audio",
                path=path,
                mime_type=mime_type,
                caption=f"[Audio Transcript]: {transcript}"
            )

        except asyncio.TimeoutError:
            logger.error("Sarvam transcription timed out after %ds (attempt %d)", TRANSCRIBE_TIMEOUT_SECONDS, attempt)
            last_error = asyncio.TimeoutError(
                f"Transcription timed out after {TRANSCRIBE_TIMEOUT_SECONDS}s"
            )
            break  # Timeout is not retryable

        except ApiError as e:
            logger.error("Sarvam API error on attempt %d: status=%s body=%s", attempt, e.status_code, e.body)
            last_error = e
            # Retry only on 5xx server-side errors
            if e.status_code and e.status_code >= 500 and attempt <= MAX_RETRIES:
                await asyncio.sleep(RETRY_DELAY_SECONDS * attempt)
                continue
            break  # 4xx or unknown — don't retry

        except OSError as e:
            logger.error("Failed to read audio file %s: %s", path, e)
            last_error = e
            break  # File I/O errors are not retryable

        except Exception as e:
            logger.exception("Unexpected error during audio transcription (attempt %d)", attempt)
            last_error = e
            break

    return IncomingMessage(
        type="audio",
        path=path,
        mime_type=mime_type,
        caption=f"[Audio Transcription Error]: {last_error}"
    )
