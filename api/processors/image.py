import os
import asyncio
import base64
import logging
from typing import Optional
from openai import AsyncOpenAI, APIStatusError, APITimeoutError, APIConnectionError
from agent import IncomingMessage

logger = logging.getLogger(__name__)

# Module-level singleton — created once, reused for all requests
client = AsyncOpenAI()

# OpenAI vision limits: max 20 MB per image
MAX_IMAGE_SIZE_MB = 20
MAX_IMAGE_SIZE_BYTES = MAX_IMAGE_SIZE_MB * 1024 * 1024

# Timeout for the OpenAI vision API call (seconds)
VISION_TIMEOUT_SECONDS = 30

# Number of retries on transient server errors (5xx / connection errors)
MAX_RETRIES = 2
RETRY_DELAY_SECONDS = 2


def encode_image(image_path: str) -> str:
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


async def process_image(path, caption: Optional[str], mime_type: Optional[str]) -> IncomingMessage:
  
    # --- Guard: file must exist ---
    if not path or not os.path.exists(path):
        logger.warning("Image file not found: %s", path)
        return IncomingMessage(
            type="image",
            path=path,
            caption="[Image Error]: The uploaded image could not be loaded or was corrupted. Please ask the user to re-upload the image.",
            mime_type=mime_type
        )

    # --- Guard: file size ---
    file_size = os.path.getsize(path)
    if file_size > MAX_IMAGE_SIZE_BYTES:
        size_mb = file_size / (1024 * 1024)
        logger.warning("Image file too large: %.1f MB (limit %d MB)", size_mb, MAX_IMAGE_SIZE_MB)
        return IncomingMessage(
            type="image",
            path=path,
            caption=f"[Image Error]: File is too large ({size_mb:.1f} MB). Maximum allowed is {MAX_IMAGE_SIZE_MB} MB.",
            mime_type=mime_type
        )

    # If a caption was already provided (e.g. user typed one), use it directly
    if caption:
        return IncomingMessage(
            type="image",
            path=path,
            caption=caption,
            mime_type=mime_type
        )

    last_error: Exception | None = None

    for attempt in range(1, MAX_RETRIES + 2):  # attempts: 1, 2, 3
        try:
            # Encode image to base64 (blocking I/O — run in thread to avoid blocking event loop)
            base64_image = await asyncio.get_event_loop().run_in_executor(None, encode_image, path)

            effective_mime = mime_type or "image/jpeg"
            user_content = [
                {
                    "type": "text",
                    "text": ("Analyze the image and write a single short sentence (10-15 words) asking the user "
                            "if they want to save it, identifying what the image shows. "
                            "Example format: 'Ask the user. You uploaded [short description of image]. Do you want to save it?' "
                            "Do not add any additional text or commentary.")
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{effective_mime};base64,{base64_image}"
                    }
                }
            ]

            response = await asyncio.wait_for(
                client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": user_content}],
                    max_tokens=60,  # Short description only — prevent over-spending tokens
                ),
                timeout=VISION_TIMEOUT_SECONDS
            )

            description = (response.choices[0].message.content or "").strip()
            if not description:
                logger.warning("OpenAI returned an empty description for: %s", path)
                description = "Ask the user. You uploaded an image. Do you want to save it?"

            return IncomingMessage(
                type="image",
                path=path,
                caption=description,
                mime_type=mime_type
            )

        except asyncio.TimeoutError:
            logger.error("OpenAI vision timed out after %ds (attempt %d)", VISION_TIMEOUT_SECONDS, attempt)
            last_error = asyncio.TimeoutError(f"Image analysis timed out after {VISION_TIMEOUT_SECONDS}s")
            break  # Timeout is not retryable

        except APITimeoutError as e:
            logger.error("OpenAI API timeout on attempt %d: %s", attempt, e)
            last_error = e
            break

        except APIConnectionError as e:
            logger.error("OpenAI connection error on attempt %d: %s", attempt, e)
            last_error = e
            if attempt <= MAX_RETRIES:
                await asyncio.sleep(RETRY_DELAY_SECONDS * attempt)
                continue
            break

        except APIStatusError as e:
            logger.error("OpenAI API error on attempt %d: status=%s message=%s", attempt, e.status_code, e.message)
            last_error = e
            # Retry only on 5xx server-side errors
            if e.status_code >= 500 and attempt <= MAX_RETRIES:
                await asyncio.sleep(RETRY_DELAY_SECONDS * attempt)
                continue
            break  # 4xx (bad request, quota, etc.) — don't retry

        except OSError as e:
            logger.error("Failed to read image file %s: %s", path, e)
            last_error = e
            break  # File I/O errors are not retryable

        except Exception as e:
            logger.exception("Unexpected error during image analysis (attempt %d)", attempt)
            last_error = e
            break

    return IncomingMessage(
        type="image",
        path=path,
        caption="[Image Error]: User uploaded the image without caption. Unable to analyze the image to understand the content due to a temporary issue. Please ask the user if they want to save this image.",
        mime_type=mime_type
    )
