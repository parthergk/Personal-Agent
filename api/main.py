import logging
import os
import re
from datetime import datetime
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query, Request, Response, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from agent import process_message, IncomingMessage
from processors import preprocess_message
from services import (
    start_scheduler,
    stop_scheduler,
    get_msg,
    send_whatsapp_message,
    mark_as_read_and_typing,
    get_otp,
    verify_otp,
    clean_phone,
    verifying_authentication,
    set_user_auth_cache,
)
from db.setup import setup_qdrant
from db.session import Base, engine, get_db
from db.models.user import User


load_dotenv()

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure database tables exist
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        logger.warning("Could not auto-create tables: %s", e)
    
    try:
        setup_qdrant()
    except Exception as e:
        logger.warning("Could not setup Qdrant collection: %s", e)

    # Start reminder scheduler on startup (every 5 seconds)
    start_scheduler(interval_seconds=5)
    yield
    # Stop scheduler on shutdown
    stop_scheduler()


app = FastAPI(lifespan=lifespan)

# Allow CORS for Next.js frontend or other clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", os.getenv("FRONTEND_URL")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



def normalize_phone(phone: str) -> str:
    """Normalize phone string to a consistent format (+<digits>)."""
    cleaned = re.sub(r"[^\d+]", "", phone.strip())
    if not cleaned.startswith("+"):
        cleaned = "+" + cleaned
    return cleaned



class ChatRequest(BaseModel):
    message: IncomingMessage


@app.post("/chat")
async def chat(request: ChatRequest):

    preprocess_response = await preprocess_message(request.message)
    logger.debug("preprocess response: %s", preprocess_response)
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

    logger.debug("[WhatsApp Webhook Received]: %s", data)

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

                    # Verify sender authentication (registered and verified)
                    auth_user = await verifying_authentication(sender) if sender else None
                    if not auth_user:
                        continue

                    # 1. Parse raw webhook message into structured IncomingMessage (like getMsg.ts)
                    incoming_msg = await get_msg(message)
                    if not incoming_msg:
                        continue

                    # 2. Preprocess (image analysis, Sarvam audio transcription, documents, etc.)
                    preprocess_response = await preprocess_message(incoming_msg)

                    # 3. Process with LLM Agent
                    response = await process_message(preprocess_response, user_id=auth_user.get("user_id"))

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


class RegisterRequest(BaseModel):
    phone: str
    name: str | None = None


class VerifyOtpRequest(BaseModel):
    phone: str
    otp: str
    name: str | None = None


@app.post("/register")
@app.post("/send-otp")
async def register_or_send_otp(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    1. Check user table:
       - If user exists and is active: return "You are already registered"
       - If user exists with same number but not active: send OTP
       - If user does not exist: store user in DB with is_active=False and send OTP
    2. Use otp_service to generate and store OTP with cooldown rate-limiting.
    """
    if not request.phone or len(request.phone.strip()) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide a valid phone number",
        )

    normalized_phone = clean_phone(request.phone)

    # Validate E.164 international phone number format (+<country_code><digits>)
    if not re.match(r"^\+[1-9]\d{7,14}$", normalized_phone):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid phone number format. Please include country code (e.g. +91 98765 43210).",
        )

    # 1. Check user table
    user = db.query(User).filter(User.phone == normalized_phone).first()

    # If user exists and is already active: return you are already registered
    if user and user.is_active:
        return {
            "success": False,
            "already_registered": True,
            "message": "You are already registered",
            "phone": normalized_phone,
        }

    # If user exists but is not active: update name if provided
    if user and not user.is_active:
        if request.name:
            user.name = request.name.strip()
            user.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(user)

    # If user does not exist with the number: store initially in DB with is_active=False
    if not user:
        name_to_use = request.name.strip() if request.name else f"User {normalized_phone[-4:]}"
        user = User(
            phone=normalized_phone,
            name=name_to_use,
            timezone="Asia/Kolkata",
            is_active=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info("Created inactive user %s pending OTP verification", normalized_phone)

    # 2. Use otp_service to generate and store OTP with cooldown rate-limiting
    otp, remaining = await get_otp(normalized_phone)

    if remaining > 0:
        return {
            "success": False,
            "cooldown": True,
            "remaining_seconds": remaining,
            "message": f"Please wait {remaining} seconds before requesting a new code.",
            "phone": normalized_phone,
        }

    # Dispatch OTP via WhatsApp if configured
    whatsapp_recipient = re.sub(r"\D", "", normalized_phone)
    try:
        await send_whatsapp_message(
            to=whatsapp_recipient,
            message=f"Your Vxyak verification code is: {otp}. It is valid for 5 minutes.",
        )
        logger.info("Sent WhatsApp verification OTP to %s", whatsapp_recipient)
    except Exception as e:
        logger.warning("WhatsApp OTP dispatch could not be delivered: %s", e)

    is_production = os.getenv("ENVIRONMENT", "development").lower() == "production"

    response_data = {
        "success": True,
        "message": "Verification code sent successfully",
        "phone": normalized_phone,
    }

    # Expose dummy code only outside production for testing convenience
    if not is_production:
        response_data["dummy_code"] = "123456"

    return response_data


@app.post("/verify-otp")
async def verify_user_otp(request: VerifyOtpRequest, db: Session = Depends(get_db)):
    """
    Verifies OTP via otp_service and activates the user in the database.
    """
    if not request.phone or not request.otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number and OTP code are required",
        )

    normalized_phone = clean_phone(request.phone)
    entered_otp = request.otp.strip()

    # 1. Verify OTP with otp_service
    is_valid, reason = await verify_otp(normalized_phone, entered_otp)
    if not is_valid:
        if reason == "too_many_attempts":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Too many incorrect attempts. Please request a new verification code.",
            )
        elif reason == "expired":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Verification code has expired. Please request a new one.",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification code. Please check and try again.",
            )

    # 2. Activate user in DB
    user = db.query(User).filter(User.phone == normalized_phone).first()

    if not user:
        user = User(
            phone=normalized_phone,
            name=request.name.strip() if request.name else f"User {normalized_phone[-4:]}",
            timezone="Asia/Kolkata",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(user)
    else:
        user.is_active = True
        if request.name:
            user.name = request.name.strip()
        user.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(user)
    logger.info("User verified and activated: %s (id: %s)", normalized_phone, user.id)

    # Immediately cache active auth status in Redis
    try:
        await set_user_auth_cache(user_id=user.id, phone=normalized_phone, is_active=True, name=user.name)
    except Exception as e:
        logger.warning("Could not set Redis auth cache on verification: %s", e)

    return {
        "success": True,
        "message": "User verified and activated successfully",
        "user": {
            "id": user.id,
            "phone": user.phone,
            "name": user.name,
            "timezone": user.timezone,
            "is_active": user.is_active,
        },
    }
