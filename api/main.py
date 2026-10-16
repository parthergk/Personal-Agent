import logging
import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query, status
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from agent import process_message, IncomingMessage
from processors import preprocess_message
from services.reminder_scheduler import start_scheduler, stop_scheduler

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

    preprocess_response = preprocess_message(request.message)
    print("\n\npreprocess response", preprocess_response)
    response = process_message(preprocess_response)

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
