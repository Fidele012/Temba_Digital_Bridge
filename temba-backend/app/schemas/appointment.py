from uuid import UUID
from datetime import date, datetime

from pydantic import Field

from app.models.appointment import AppointmentReason, AppointmentStatus, MeetingType
from app.schemas.common import ORMModel


class AppointmentCreate(ORMModel):
    provider_id: UUID
    reason: AppointmentReason
    meeting_type: MeetingType = MeetingType.IN_PERSON
    appointment_date: date
    appointment_time: str = Field(pattern=r"^\d{2}:\d{2}$")
    notes: str | None = None


class AppointmentRescheduleRequest(ORMModel):
    """Community member requests a new slot."""
    requested_date: date
    requested_time: str = Field(pattern=r"^\d{2}:\d{2}$")
    reschedule_reason: str | None = None


class ProviderRescheduleProposal(ORMModel):
    """Provider proposes an alternative slot."""
    proposed_date: date
    proposed_time: str = Field(pattern=r"^\d{2}:\d{2}$")
    proposed_message: str | None = None


class AppointmentStatusUpdate(ORMModel):
    status: AppointmentStatus
    provider_note: str | None = None


class AppointmentPublic(ORMModel):
    id: UUID
    user_id: UUID
    provider_id: UUID
    reason: AppointmentReason
    meeting_type: MeetingType
    status: AppointmentStatus
    notes: str | None
    appointment_date: date
    appointment_time: str
    requested_date: date | None
    requested_time: str | None
    reschedule_reason: str | None
    proposed_date: date | None
    proposed_time: str | None
    proposed_message: str | None
    provider_note: str | None
    created_at: datetime
    updated_at: datetime
    sla_deadline: datetime | None = None
    overdue_flagged: bool = False
    resolution_submitted_at: datetime | None = None
    verified_at: datetime | None = None
    user_name: str | None = None
    user_phone: str | None = None
    provider_name: str | None = None
