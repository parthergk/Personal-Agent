import logging
import os
import re
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from db.models.user import User
from db.session import get_db
from services import (
    clean_phone,
    get_otp,
    send_whatsapp_message,
    set_user_auth_cache,
    verify_otp,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Auth"])


class RegisterRequest(BaseModel):
    phone: str
    name: str | None = None


class VerifyOtpRequest(BaseModel):
    phone: str
    otp: str
    name: str | None = None


@router.post("/register")
@router.post("/send-otp")
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


@router.post("/verify-otp")
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
