from uuid import UUID
from datetime import datetime

from app.models.notification import NotificationType
from app.schemas.common import ORMModel


class NotificationPublic(ORMModel):
    id: UUID
    notification_type: NotificationType
    title: str
    body: str
    is_read: bool
    reference_id: str | None
    reference_type: str | None
    created_at: datetime


class AnnouncementCreate(ORMModel):
    title: str
    body: str
    audience: str = "all"
    is_pinned: bool = False


class AnnouncementPublic(ORMModel):
    id: UUID
    title: str
    body: str
    audience: str
    is_pinned: bool
    is_published: bool
    created_at: datetime
