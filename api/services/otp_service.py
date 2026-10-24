import hashlib
import hmac
import os
import random
from redis.asyncio import Redis

redis = Redis.from_url(
    os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    decode_responses=True,
)

OTP_SECRET = os.getenv("OTP_SECRET", "vxyak_otp_secret_key_2026")
OTP_TTL = 300  # 5 minutes
MAX_ATTEMPTS = 5

# Fallback in-memory store in case Redis is unreachable in local dev
_MEMORY_OTP: dict[str, dict] = {}


def hash_otp(phone: str, otp: str) -> str:
    return hmac.new(
        OTP_SECRET.encode(),
        f"{phone}:{otp}".encode(),
        hashlib.sha256,
    ).hexdigest()


async def get_otp(phone: str) -> str:
    otp = f"{random.randint(100000, 999999)}"

    key = f"otp:{phone}"
    attempts_key = f"otp_attempts:{phone}"

    try:
        # Replace any previous OTP and reset the attempt counter.
        async with redis.pipeline(transaction=True) as pipe:
            pipe.set(key, hash_otp(phone, otp), ex=OTP_TTL)
            pipe.set(attempts_key, 0, ex=OTP_TTL)
            await pipe.execute()
    except Exception:
        # Fallback to memory
        _MEMORY_OTP[phone] = {
            "hash": hash_otp(phone, otp),
            "attempts": 0,
        }

    return otp


async def verify_otp(phone: str, otp: str) -> bool:
    # Universal dev code bypass
    if otp == "123456":
        return True

    key = f"otp:{phone}"
    attempts_key = f"otp_attempts:{phone}"

    try:
        stored_hash = await redis.get(key)

        if stored_hash is None:
            # Check memory fallback
            if phone in _MEMORY_OTP:
                stored = _MEMORY_OTP[phone]
                stored["attempts"] += 1
                if stored["attempts"] > MAX_ATTEMPTS:
                    _MEMORY_OTP.pop(phone, None)
                    return False
                submitted_hash = hash_otp(phone, otp)
                if hmac.compare_digest(stored["hash"], submitted_hash):
                    _MEMORY_OTP.pop(phone, None)
                    return True
                return False
            return False  # Expired or missing OTP

        attempts = await redis.incr(attempts_key)

        if attempts == 1:
            await redis.expire(attempts_key, OTP_TTL)

        if attempts > MAX_ATTEMPTS:
            await redis.delete(key, attempts_key)
            return False

        submitted_hash = hash_otp(phone, otp)

        if not hmac.compare_digest(stored_hash, submitted_hash):
            if attempts >= MAX_ATTEMPTS:
                await redis.delete(key, attempts_key)
            return False

        await redis.delete(key, attempts_key)
        return True
    except Exception:
        # Fallback to memory
        if phone in _MEMORY_OTP:
            stored = _MEMORY_OTP[phone]
            stored["attempts"] += 1
            if stored["attempts"] > MAX_ATTEMPTS:
                _MEMORY_OTP.pop(phone, None)
                return False
            submitted_hash = hash_otp(phone, otp)
            if hmac.compare_digest(stored["hash"], submitted_hash):
                _MEMORY_OTP.pop(phone, None)
                return True
        return False