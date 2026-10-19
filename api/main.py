import logging
import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query, Request, Response, status
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from agent import process_message, IncomingMessage
from processors import preprocess_message
from services import (
    start_scheduler,
    stop_scheduler,
    get_msg,
    send_whatsapp_message,
    mark_as_read_and_typing,
)

load_dotenv()

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start reminder scheduler on startup (every 5 seconds)
    start_scheduler(interval_seconds=5)
    yield
    # Stop scheduler on shutdown
    stop_scheduler()


app = FastAPI(lifespan=lifespan)


class ChatRequest(BaseModel):
    message: IncomingMessage


@app.post("/chat")
async def chat(request: ChatRequest):

    preprocess_response = await preprocess_message(request.message)
    print("\n\npreprocess response", preprocess_response)
    response = await process_message(preprocess_response)

    return {
        "response": response
    }


@app.get("/webhook")
async def verify_webhook(
    mode: str | None = Query(None, alias="hub.mode"),
    token: str | None = Query(None, alias="hub.verify_token"),
    challenge: str | None = Query(None, alias="hub.challenge"),
):
    """WhatsApp Business API Webhook verification (Meta Cloud API).

    Meta sends a GET request with hub.mode, hub.verify_token, and hub.challenge
    to verify endpoint ownership.
    """
    verify_token = os.getenv("WHATSAPP_VERIFY_TOKEN")

    if mode == "subscribe" and verify_token and token == verify_token:
        logger.info("WhatsApp webhook verified successfully.")
        return PlainTextResponse(content=challenge or "", status_code=status.HTTP_200_OK)

    logger.warning("WhatsApp webhook verification failed: mode=%s, token_match=%s", mode, token == verify_token)
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Verification token mismatch",
    )


@app.post("/webhook")
async def receive_webhook(request: Request):
    try:
        data = await request.json()
    except Exception:
        data = await request.body()

    print("\n[WhatsApp Webhook Received]:", data)

    # Process individual messages if present in the payload
    if isinstance(data, dict):
        for entry in data.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                for message in value.get("messages", []):
                    sender = message.get("from")
                    message_id = message.get("id")

                    # Mark message as read (blue ticks) and show typing indicator immediately
                    if message_id:
                        await mark_as_read_and_typing(message_id)

                    # 1. Parse raw webhook message into structured IncomingMessage (like getMsg.ts)
                    incoming_msg = await get_msg(message)
                    if not incoming_msg:
                        continue

                    # 2. Preprocess (image analysis, Sarvam audio transcription, documents, etc.)
                    preprocess_response = await preprocess_message(incoming_msg)

                    # 3. Process with LLM Agent
                    response = await process_message(preprocess_response, sender=sender)

                    # 4. Sending response back to user (matching whatsapp/index.ts)
                    res_type = getattr(response, "type", None) or (response.get("type") if isinstance(response, dict) else "text")
                    res_path = getattr(response, "path", None) or (response.get("path") if isinstance(response, dict) else None)
                    clean_text = getattr(response, "message", None) or (response.get("message") if isinstance(response, dict) else (response if isinstance(response, str) else ""))

                    # Resolve relative file path if necessary
                    if res_path and not os.path.isabs(res_path) and not os.path.exists(res_path):
                        candidate = os.path.join(os.path.dirname(__file__), res_path)
                        if os.path.exists(candidate):
                            res_path = candidate

                    if sender:
                        if res_type == "image":
                            image_path = res_path
                            if image_path and os.path.exists(image_path):
                                await send_whatsapp_message(to=sender, message=clean_text, type="image", path=image_path)
                            elif clean_text:
                                await send_whatsapp_message(to=sender, message=clean_text)

                        elif res_type == "video":
                            video_path = res_path
                            if video_path and os.path.exists(video_path):
                                await send_whatsapp_message(to=sender, message=clean_text, type="video", path=video_path)
                            elif clean_text:
                                await send_whatsapp_message(to=sender, message=clean_text)

                        elif res_type == "document":
                            doc_path = res_path
                            if doc_path and os.path.exists(doc_path):
                                await send_whatsapp_message(to=sender, message=clean_text, type="document", path=doc_path)
                            elif clean_text:
                                await send_whatsapp_message(to=sender, message=clean_text)

                        elif res_type == "audio":
                            audio_path = res_path
                            if audio_path and os.path.exists(audio_path):
                                await send_whatsapp_message(to=sender, message=clean_text, type="audio", path=audio_path)
                            elif clean_text:
                                await send_whatsapp_message(to=sender, message=clean_text)

                        else:
                            if clean_text:
                                await send_whatsapp_message(to=sender, message=clean_text)

    return Response(content="EVENT_RECEIVED", status_code=status.HTTP_200_OK)
