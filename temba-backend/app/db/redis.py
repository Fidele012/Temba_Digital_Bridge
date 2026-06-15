"""Redis client — used for refresh token storage and rate limiting."""
from redis.asyncio import Redis

from app.core.config import settings

_redis: Redis | None = None


async def get_redis() -> Redis:
    global _redis
    if _redis is None:
        _redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis


async def close_redis() -> None:
    global _redis
    if _redis:
        await _redis.aclose()
        _redis = None


# ── Token blacklist / refresh-token store ────────────────────────────────────

REFRESH_PREFIX = "rt:"
BLACKLIST_PREFIX = "bl:"


async def store_refresh_token(user_id: str, token: str, ttl_seconds: int) -> None:
    r = await get_redis()
    await r.setex(f"{REFRESH_PREFIX}{user_id}", ttl_seconds, token)


async def get_stored_refresh_token(user_id: str) -> str | None:
    r = await get_redis()
    return await r.get(f"{REFRESH_PREFIX}{user_id}")


async def delete_refresh_token(user_id: str) -> None:
    r = await get_redis()
    await r.delete(f"{REFRESH_PREFIX}{user_id}")


async def blacklist_token(jti: str, ttl_seconds: int) -> None:
    r = await get_redis()
    await r.setex(f"{BLACKLIST_PREFIX}{jti}", ttl_seconds, "1")


async def is_token_blacklisted(jti: str) -> bool:
    r = await get_redis()
    return await r.exists(f"{BLACKLIST_PREFIX}{jti}") == 1


# ── Password-reset OTP store ──────────────────────────────────────────────────

OTP_PREFIX = "pwd_otp:"
OTP_TTL_SECONDS = 900  # 15 minutes


async def store_reset_otp(user_id: str, otp: str) -> None:
    r = await get_redis()
    await r.setex(f"{OTP_PREFIX}{user_id}", OTP_TTL_SECONDS, otp)


async def get_reset_otp(user_id: str) -> str | None:
    r = await get_redis()
    return await r.get(f"{OTP_PREFIX}{user_id}")


async def delete_reset_otp(user_id: str) -> None:
    r = await get_redis()
    await r.delete(f"{OTP_PREFIX}{user_id}")
