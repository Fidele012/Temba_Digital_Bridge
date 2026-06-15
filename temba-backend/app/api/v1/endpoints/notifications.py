"""
Notification endpoints.
GET    /notifications              → list own (community/provider)
PUT    /notifications/{id}/read    → mark read
PUT    /notifications/read-all     → mark all read
DELETE /notifications/{id}

Announcement endpoints (nested here for simplicity).
GET    /announcements              → list (public)
POST   /announcements              → create (admin)
DELETE /announcements/{id}         → admin
"""
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, require_admin
from app.db.session import get_db
from app.models.announcement import Announcement
from app.models.notification import Notification
from app.models.user import User
from app.schemas.common import MessageResponse, PaginatedResponse, PaginationParams
from app.schemas.notification import AnnouncementCreate, AnnouncementPublic, NotificationPublic

router = APIRouter(tags=["notifications"])


# ── Notifications ─────────────────────────────────────────────────────────────

@router.get("/notifications", response_model=PaginatedResponse[NotificationPublic])
async def list_notifications(
    params: Annotated[PaginationParams, Depends()],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    q = select(Notification).where(Notification.user_id == current_user.id)
    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
    result = await db.execute(q.order_by(Notification.created_at.desc()).offset(params.offset).limit(params.size))
    return {
        "items": result.scalars().all(),
        "total": total,
        "page": params.page,
        "size": params.size,
        "pages": -(-total // params.size),
    }


@router.put("/notifications/{notif_id}/read", response_model=MessageResponse)
async def mark_read(
    notif_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    result = await db.execute(select(Notification).where(Notification.id == notif_id))
    notif = result.scalar_one_or_none()
    if not notif or notif.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    notif.is_read = True
    return {"message": "Marked as read"}


@router.put("/notifications/read-all", response_model=MessageResponse)
async def mark_all_read(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    await db.execute(
        update(Notification)
        .where(Notification.user_id == current_user.id, Notification.is_read == False)  # noqa: E712
        .values(is_read=True)
    )
    return {"message": "All notifications marked as read"}


@router.delete("/notifications/{notif_id}", response_model=MessageResponse)
async def delete_notification(
    notif_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    result = await db.execute(select(Notification).where(Notification.id == notif_id))
    notif = result.scalar_one_or_none()
    if not notif or notif.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    await db.delete(notif)
    return {"message": "Notification deleted"}


# ── Announcements ─────────────────────────────────────────────────────────────

@router.get("/announcements", response_model=list[AnnouncementPublic])
async def list_announcements(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[Announcement]:
    result = await db.execute(
        select(Announcement)
        .where(Announcement.is_published == True)  # noqa: E712
        .order_by(Announcement.is_pinned.desc(), Announcement.created_at.desc())
        .limit(50)
    )
    return result.scalars().all()


@router.post("/announcements", response_model=AnnouncementPublic, status_code=status.HTTP_201_CREATED)
async def create_announcement(
    body: AnnouncementCreate,
    admin: Annotated[User, Depends(require_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Announcement:
    ann = Announcement(author_id=admin.id, **body.model_dump())
    db.add(ann)
    await db.flush()
    return ann


@router.delete("/announcements/{ann_id}", response_model=MessageResponse)
async def delete_announcement(
    ann_id: UUID,
    admin: Annotated[User, Depends(require_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    result = await db.execute(select(Announcement).where(Announcement.id == ann_id))
    ann = result.scalar_one_or_none()
    if not ann:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Announcement not found")
    await db.delete(ann)
    return {"message": "Announcement deleted"}
