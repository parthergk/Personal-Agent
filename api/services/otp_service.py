import hashlib
import hmac
import os
import random
import re
import time
from typing import Tuple
from redis.asyncio import Redis

redis = Redis.from_url(
    os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    decode_responses=True,
)

OTP_SECRET = os.getenv("OTP_SECRET", "vxyak_otp_secret_key_2026")
OTP_TTL = 300  # 5 minutes
COOLDOWN_TTL = 60  # 60 seconds cooldown between OTP requests
MAX_ATTEMPTS = 5

# Fallback in-memory store in case Redis is unreachable in local dev
_MEMORY_OTP: dict[str, dict] = {}
_MEMORY_COOLDOWN: dict[str, float] = {}


def clean_phone(phone: str) -> str:
    """Normalize phone to +<digits> format."""
    cleaned = re.sub(r"[^\d+]", "", phone.strip())
    if not cleaned.startswith("+"):
        cleaned = "+" + cleaned
    return cleaned


def hash_otp(phone: str, otp: str) -> str:
    normalized = clean_phone(phone)
    return hmac.new(
        OTP_SECRET.encode(),
        f"{normalized}:{otp}".encode(),
        hashlib.sha256,
    ).hexdigest()


async def check_cooldown(phone: str) -> int:
    """Returns remaining seconds if rate-limited, or 0 if allowed."""
    normalized = clean_phone(phone)
    key = f"otp_cooldown:{normalized}"

    try:
        ttl = await redis.ttl(key)
        if ttl and ttl > 0:
            return ttl
    except Exception:
        # Check memory cooldown
        if normalized in _MEMORY_COOLDOWN:
            expires_at = _MEMORY_COOLDOWN[normalized]
            remaining = int(expires_at - time.time())
            if remaining > 0:
                return remaining
            else:
                _MEMORY_COOLDOWN.pop(normalized, None)
    return 0


async def get_otp(phone: str, ignore_cooldown: bool = False) -> Tuple[str, int]:
    """
    Generates and stores a 6-digit OTP.
    Returns (otp_string, cooldown_remaining_seconds).
    If cooldown is active and ignore_cooldown is False, returns ("", remaining_seconds).
    """
    normalized = clean_phone(phone)

    if not ignore_cooldown:
        remaining = await check_cooldown(normalized)
        if remaining > 0:
            return "", remaining

    otp = f"{random.randint(100000, 999999)}"

    key = f"otp:{normalized}"
    attempts_key = f"otp_attempts:{normalized}"
    cooldown_key = f"otp_cooldown:{normalized}"

    try:
        async with redis.pipeline(transaction=True) as pipe:
            pipe.set(key, hash_otp(normalized, otp), ex=OTP_TTL)
            pipe.set(attempts_key, 0, ex=OTP_TTL)
            pipe.set(cooldown_key, 1, ex=COOLDOWN_TTL)
            await pipe.execute()
    except Exception:
        # Fallback to in-memory store
        _MEMORY_OTP[normalized] = {
            "hash": hash_otp(normalized, otp),
            "attempts": 0,
            "expires_at": time.time() + OTP_TTL,
        }
        _MEMORY_COOLDOWN[normalized] = time.time() + COOLDOWN_TTL

    return otp, 0


async def verify_otp(phone: str, otp: str) -> Tuple[bool, str]:
    """
    Verifies the provided OTP against the stored hash.
    Returns (is_valid: bool, reason: str).
    """
    normalized = clean_phone(phone)
    entered_otp = otp.strip()

    # Universal dev code bypass: disabled in production
    is_production = os.getenv("ENVIRONMENT", "development").lower() == "production"
    allow_dev_otp = os.getenv("ALLOW_DEV_OTP", "true").lower() == "true" and not is_production

    if allow_dev_otp and entered_otp == "123456":
        return True, "verified"

    key = f"otp:{normalized}"
    attempts_key = f"otp_attempts:{normalized}"

    try:
        stored_hash = await redis.get(key)

        if stored_hash is None:
            # Check in-memory fallback
            if normalized in _MEMORY_OTP:
                stored = _MEMORY_OTP[normalized]
                if time.time() > stored.get("expires_at", 0):
                    _MEMORY_OTP.pop(normalized, None)
                    return False, "expired"

                stored["attempts"] += 1
                if stored["attempts"] > MAX_ATTEMPTS:
                    _MEMORY_OTP.pop(normalized, None)
                    return False, "too_many_attempts"

                submitted_hash = hash_otp(normalized, entered_otp)
                if hmac.compare_digest(stored["hash"], submitted_hash):
                    _MEMORY_OTP.pop(normalized, None)
                    return True, "verified"
                return False, "invalid"
            return False, "expired"

        attempts = await redis.incr(attempts_key)

        if attempts == 1:
            await redis.expire(attempts_key, OTP_TTL)

        if attempts > MAX_ATTEMPTS:
            await redis.delete(key, attempts_key)
            return False, "too_many_attempts"

        submitted_hash = hash_otp(normalized, entered_otp)

        if not hmac.compare_digest(stored_hash, submitted_hash):
            if attempts >= MAX_ATTEMPTS:
                await redis.delete(key, attempts_key)
                return False, "too_many_attempts"
            return False, "invalid"

        await redis.delete(key, attempts_key)
        return True, "verified"
    except Exception:
        # Fallback to memory
        if normalized in _MEMORY_OTP:
            stored = _MEMORY_OTP[normalized]
            if time.time() > stored.get("expires_at", 0):
                _MEMORY_OTP.pop(normalized, None)
                return False, "expired"

            stored["attempts"] += 1
            if stored["attempts"] > MAX_ATTEMPTS:
                _MEMORY_OTP.pop(normalized, None)
                return False, "too_many_attempts"

            submitted_hash = hash_otp(normalized, entered_otp)
            if hmac.compare_digest(stored["hash"], submitted_hash):
                _MEMORY_OTP.pop(normalized, None)
                return True, "verified"
            return False, "invalid"
        return False, "expired"