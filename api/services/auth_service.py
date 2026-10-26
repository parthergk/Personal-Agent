import json
import logging
import time
from typing import Optional
from db.session import SessionLocal
from db.models.user import User
from .otp_service import redis, clean_phone
from .whatsapp import send_whatsapp_message

logger = logging.getLogger(__name__)

# Fallback in-memory cache if Redis is unavailable in local dev
_MEMORY_AUTH: dict[str, tuple[dict, float]] = {}
_MEMORY_NOTICE_COOLDOWN: dict[str, float] = {}

AUTH_CACHE_TTL = 3600  # 1 hour for active users
NEGATIVE_CACHE_TTL = 180  # 3 minutes for unregistered / inactive
NOTICE_COOLDOWN_TTL = 60  # 60 seconds cooldown to prevent spamming WhatsApp rejection messages

AUTH_UNREGISTERED_MESSAGE = (
    "👋 You are not authenticated right now.\n\n"
    "Please visit our website to register and verify your account:\n"
    "👉 https://vxyak.vercel.app/\n\n"
    "Once verified, you can start using your personal assistant!"
)


async def set_user_auth_cache(
    user_id: int,
    phone: str,
    is_active: bool,
    name: Optional[str] = None,
    ttl: int = AUTH_CACHE_TTL,
) -> None:
    """
    Sets or updates the user authentication status in Redis cache and in-memory fallback.
    """
    normalized = clean_phone(phone)
    key = f"user:auth:{normalized}"
    payload = {
        "user_id": user_id,
        "phone": normalized,
        "name": name or "",
        "is_active": is_active,
    }
    payload_str = json.dumps(payload)

    try:
        await redis.set(key, payload_str, ex=ttl)
    except Exception:
        _MEMORY_AUTH[normalized] = (payload, time.time() + ttl)


async def _get_cached_auth(phone: str) -> Optional[dict]:
    """
    Retrieves user authentication data from Redis or in-memory fallback.
    """
    normalized = clean_phone(phone)
    key = f"user:auth:{normalized}"

    try:
        cached = await redis.get(key)
        if cached:
            return json.loads(cached)
    except Exception:
        if normalized in _MEMORY_AUTH:
            data, expires_at = _MEMORY_AUTH[normalized]
            if time.time() < expires_at:
                return data
            else:
                _MEMORY_AUTH.pop(normalized, None)

    return None


async def _should_send_notice(phone: str) -> bool:
    """
    Checks and sets a rate-limiting cooldown for the WhatsApp rejection message.
    """
    normalized = clean_phone(phone)
    key = f"auth:notice_cooldown:{normalized}"

    try:
        exists = await redis.get(key)
        if exists:
            return False
        await redis.set(key, "1", ex=NOTICE_COOLDOWN_TTL)
        return True
    except Exception:
        now = time.time()
        last_sent = _MEMORY_NOTICE_COOLDOWN.get(normalized, 0)
        if now - last_sent < NOTICE_COOLDOWN_TTL:
            return False
        _MEMORY_NOTICE_COOLDOWN[normalized] = now
        return True


async def verifying_authentication(sender: str) -> Optional[dict]:
    """
    Verifies if sender phone number is registered and activated.
    Uses Redis cache with database fallback.
    If the user is not registered or not active, sends a WhatsApp message
    directing them to register at https://vxyak.vercel.app/ and returns None.
    If authenticated, returns the user data dict: {"user_id": ..., "phone": ..., "name": ..., "is_active": True}.
    """
    if not sender:
        return None

    normalized_phone = clean_phone(sender)

    # 1. Check cache (Redis / in-memory)
    cached = await _get_cached_auth(normalized_phone)
    if cached is not None:
        if cached.get("is_active"):
            return cached
        else:
            # User was recently checked and is not active/registered
            if await _should_send_notice(normalized_phone):
                logger.info("Sender %s is not active (cached). Sending registration invite.", sender)
                try:
                    await send_whatsapp_message(to=sender, message=AUTH_UNREGISTERED_MESSAGE)
                except Exception as e:
                    logger.error("Failed to send WhatsApp registration invite to %s: %s", sender, e)
            return None

    # 2. Database lookup
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.phone == normalized_phone).first()
        if not user:
            # Also check variations just in case
            user = db.query(User).filter(User.phone.in_([sender, normalized_phone, sender.lstrip("+")])).first()

        if user and user.is_active:
            user_data = {
                "user_id": user.id,
                "phone": user.phone,
                "name": user.name,
                "is_active": True,
            }
            await set_user_auth_cache(user.id, user.phone, True, user.name, ttl=AUTH_CACHE_TTL)
            return user_data
        else:
            # Not registered or inactive
            await set_user_auth_cache(
                user_id=user.id if user else 0,
                phone=normalized_phone,
                is_active=False,
                name=user.name if user else "",
                ttl=NEGATIVE_CACHE_TTL,
            )
            if await _should_send_notice(normalized_phone):
                logger.info("Sender %s is not registered or inactive. Sending registration invite.", sender)
                try:
                    await send_whatsapp_message(to=sender, message=AUTH_UNREGISTERED_MESSAGE)
                except Exception as e:
                    logger.error("Failed to send WhatsApp registration invite to %s: %s", sender, e)
            return None

    except Exception as e:
        logger.error("Error verifying authentication for sender %s: %s", sender, e)
        return None
    finally:
        db.close()
