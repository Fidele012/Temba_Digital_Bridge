"""
User management endpoints.
GET    /users/me
PUT    /users/me
POST   /users/me/avatar
DELETE /users/me
GET    /users          (admin)
GET    /users/{id}     (admin)
PUT    /users/{id}     (admin)
DELETE /users/{id}     (admin)
"""
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, require_admin, write_audit
from app.db.session import get_db
from app.models.user import User
from app.schemas.common import MessageResponse, PaginatedResponse, PaginationParams
from app.schemas.user import UserAdminUpdate, UserPublic, UserUpdate
from app.services.file_service import upload_avatar

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserPublic)
async def get_me(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    return current_user


@router.put("/me", response_model=UserPublic)
async def update_me(
    body: UserUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(current_user, field, value)
    await write_audit(db, request, "user.update", "user", str(current_user.id), actor=current_user)
    return current_user


@router.post("/me/avatar", response_model=UserPublic)
async def upload_my_avatar(
    file: Annotated[UploadFile, File(...)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    url = await upload_avatar(file, str(current_user.id))
    current_user.avatar_url = url
    return current_user


@router.delete("/me", response_model=MessageResponse)
async def deactivate_me(
    current_user: Annotated[User, Depends(get_current_user)],
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    current_user.is_active = False
    await write_audit(db, request, "user.deactivate", "user", str(current_user.id), actor=current_user)
    return {"message": "Account deactivated"}


# ── Admin endpoints ────────────────────────────────────────────────────────────

@router.get("", response_model=PaginatedResponse[UserPublic], dependencies=[Depends(require_admin)])
async def list_users(
    params: Annotated[PaginationParams, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    total_result = await db.execute(select(func.count(User.id)))
    total = total_result.scalar_one()

    result = await db.execute(
        select(User).order_by(User.created_at.desc()).offset(params.offset).limit(params.size)
    )
    users = result.scalars().all()
    return {
        "items": users,
        "total": total,
        "page": params.page,
        "size": params.size,
        "pages": -(-total // params.size),
    }


@router.get("/{user_id}", response_model=UserPublic, dependencies=[Depends(require_admin)])
async def get_user(user_id: UUID, db: Annotated[AsyncSession, Depends(get_db)]) -> User:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserPublic, dependencies=[Depends(require_admin)])
async def admin_update_user(
    user_id: UUID,
    body: UserAdminUpdate,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    admin: Annotated[User, Depends(require_admin)],
) -> User:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(user, field, value)
    await write_audit(db, request, "admin.update_user", "user", str(user_id), actor=admin)
    return user


@router.delete("/{user_id}", response_model=MessageResponse, dependencies=[Depends(require_admin)])
async def admin_delete_user(
    user_id: UUID,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    admin: Annotated[User, Depends(require_admin)],
) -> dict:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    await db.delete(user)
    await write_audit(db, request, "admin.delete_user", "user", str(user_id), actor=admin)
    return {"message": "User deleted"}
