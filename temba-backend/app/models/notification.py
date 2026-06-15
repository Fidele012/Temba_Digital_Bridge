import enum
import uuid

from sqlalchemy import Boolean, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, TimestampMixin, UUIDMixin


class NotificationType(str, enum.Enum):
    REPORT_UPDATE = "report_update"
    SERVICE_REQUEST_UPDATE = "service_request_update"
    APPOINTMENT_UPDATE = "appointment_update"
    ANNOUNCEMENT = "announcement"
    SYSTEM = "system"


class Notification(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "notifications"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    notification_type: Mapped[NotificationType] = mapped_column(Enum(NotificationType), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    reference_id: Mapped[str | None] = mapped_column(String(36), nullable=True)  # UUID of related entity
    reference_type: Mapped[str | None] = mapped_column(String(50), nullable=True)  # "report" | "appointment" ...

    user: Mapped["User"] = relationship(back_populates="notifications")  # type: ignore[name-defined]
