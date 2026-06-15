from uuid import UUID
from datetime import datetime

from pydantic import EmailStr, Field, HttpUrl

from app.models.provider import ProviderStatus, ProviderStaffRole, ServiceCategory
from app.schemas.common import ORMModel


class ServiceAreaCreate(ORMModel):
    province: str
    district: str | None = None
    sector: str | None = None


class ServiceAreaPublic(ORMModel):
    id: UUID
    province: str
    district: str | None
    sector: str | None


class ProviderCreate(ORMModel):
    organization_name: str = Field(min_length=2, max_length=255)
    registration_number: str | None = None
    service_categories: list[str] = Field(min_length=1)
    custom_services: list[str] = Field(default_factory=list)
    description: str | None = None
    website: str | None = None
    phone: str | None = Field(None, pattern=r"^\+?[0-9]{9,15}$")
    email: EmailStr | None = None
    service_areas: list[ServiceAreaCreate] = Field(default_factory=list)


class ProviderUpdate(ORMModel):
    organization_name: str | None = Field(None, min_length=2, max_length=255)
    description: str | None = None
    website: str | None = None
    phone: str | None = Field(None, pattern=r"^\+?[0-9]{9,15}$")
    email: EmailStr | None = None
    service_categories: list[str] | None = None
    custom_services: list[str] | None = None


class AvailabilityUpdate(ORMModel):
    working_days: list[str] | None = None
    work_start_time: str | None = Field(None, pattern=r"^\d{2}:\d{2}$")
    work_end_time: str | None = Field(None, pattern=r"^\d{2}:\d{2}$")
    max_appointments_per_day: int | None = Field(None, ge=1, le=50)
    unavailable_dates: list[str] | None = None


class ProviderPublic(ORMModel):
    id: UUID
    user_id: UUID
    organization_name: str
    registration_number: str | None
    status: ProviderStatus
    service_categories: list[str]
    custom_services: list[str]
    description: str | None
    logo_url: str | None
    website: str | None
    phone: str | None
    email: str | None
    working_days: list[str]
    work_start_time: str | None
    work_end_time: str | None
    max_appointments_per_day: int
    unavailable_dates: list[str]
    service_areas: list[ServiceAreaPublic]
    created_at: datetime


class ProviderStatusUpdate(ORMModel):
    status: ProviderStatus
    reason: str | None = None


class ProviderStaffCreate(ORMModel):
    email: EmailStr
    staff_role: ProviderStaffRole


class ProviderStaffPublic(ORMModel):
    id: UUID
    provider_id: UUID
    user_id: UUID
    staff_role: ProviderStaffRole
    created_at: datetime
    # denormalised from User
    staff_name: str | None = None
    staff_email: str | None = None
