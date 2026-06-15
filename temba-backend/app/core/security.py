"""
JWT creation/verification and password hashing.
Access tokens are short-lived (15 min); refresh tokens live 7 days
and are stored in Redis so they can be revoked server-side.
"""
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ── Password helpers ───────────────────────────────────────────────────────────

def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


# ── Token helpers ──────────────────────────────────────────────────────────────

def _encode(payload: dict[str, Any]) -> str:
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def _decode(token: str) -> dict[str, Any]:
    """Raises JWTError on invalid or expired token."""
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])


def create_access_token(subject: str | UUID, role: str, extra: dict | None = None) -> str:
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": str(subject),
        "role": role,
        "type": "access",
        "iat": now,
        "exp": now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    if extra:
        payload.update(extra)
    return _encode(payload)


def create_refresh_token(subject: str | UUID, role: str) -> str:
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": str(subject),
        "role": role,
        "type": "refresh",
        "iat": now,
        "exp": now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    }
    return _encode(payload)


def decode_access_token(token: str) -> dict[str, Any]:
    data = _decode(token)
    if data.get("type") != "access":
        raise JWTError("Not an access token")
    return data


def decode_refresh_token(token: str) -> dict[str, Any]:
    data = _decode(token)
    if data.get("type") != "refresh":
        raise JWTError("Not a refresh token")
    return data
