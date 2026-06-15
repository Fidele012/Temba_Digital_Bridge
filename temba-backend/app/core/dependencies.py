"""
FastAPI dependency functions:
- get_current_user   → any authenticated user
- require_community  → community role only
- require_provider   → provider role only
- require_admin      → admin role only
- audit              → writes an AuditLog row after the response
"""
from typing import Annotated
from uuid import UUID

import structlog
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.db.redis import is_token_blacklisted
from app.db.session import get_db
from app.models.audit_log import AuditLog
from app.models.user import User, UserRole

log = structlog.get_logger(__name__)
bearer_scheme = HTTPBearer(auto_error=False)


async def _get_token_data(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> dict:
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    token = credentials.credentials
    try:
        data = decode_access_token(token)
    except JWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    jti = data.get("jti")
    if jti and await is_token_blacklisted(jti):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has been revoked")
    return data


async def get_current_user(
    token_data: Annotated[dict, Depends(_get_token_data)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    user_id = token_data.get("sub")
    result = await db.execute(select(User).where(User.id == UUID(user_id)))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")
    return user


def _role_guard(*roles: UserRole):
    async def check(user: Annotated[User, Depends(get_current_user)]) -> User:
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access requires role: {', '.join(r.value for r in roles)}",
            )
        return user
    return check


require_community = _role_guard(UserRole.COMMUNITY)
require_provider = _role_guard(UserRole.PROVIDER)
require_admin = _role_guard(UserRole.ADMIN)
require_staff = _role_guard(UserRole.PROVIDER, UserRole.ADMIN)


# ── Audit logging helper ──────────────────────────────────────────────────────

async def write_audit(
    db: AsyncSession,
    request: Request,
    action: str,
    resource_type: str,
    resource_id: str | None = None,
    actor: User | None = None,
    extra: dict | None = None,
    status_code: int | None = None,
) -> None:
    try:
        log_entry = AuditLog(
            actor_id=actor.id if actor else None,
            actor_role=actor.role.value if actor else None,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            extra=extra,
            status_code=status_code,
        )
        db.add(log_entry)
        await db.flush()
    except Exception:
        log.exception("Failed to write audit log", action=action)
