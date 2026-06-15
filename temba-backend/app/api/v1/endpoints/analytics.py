"""
Analytics & dashboard stats endpoints.
GET /analytics/overview         → platform-wide (admin)
GET /analytics/community        → community member stats
GET /analytics/provider         → provider dashboard stats
"""
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, require_admin
from app.db.session import get_db
from app.models.appointment import Appointment, AppointmentStatus
from app.models.notification import Notification
from app.models.provider import Provider
from app.models.report import Report, ReportStatus
from app.models.service_request import ServiceRequest, ServiceRequestStatus
from app.models.user import User, UserRole

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/overview")
async def platform_overview(
    admin: Annotated[User, Depends(require_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    async def count(model, *where):
        q = select(func.count(model.id))
        for w in where:
            q = q.where(w)
        return (await db.execute(q)).scalar_one()

    return {
        "total_users": await count(User),
        "community_users": await count(User, User.role == UserRole.COMMUNITY),
        "provider_users": await count(User, User.role == UserRole.PROVIDER),
        "total_providers": await count(Provider),
        "approved_providers": await count(Provider),
        "total_reports": await count(Report),
        "open_reports": await count(Report, Report.status == ReportStatus.OPEN),
        "resolved_reports": await count(Report, Report.status == ReportStatus.RESOLVED),
        "total_service_requests": await count(ServiceRequest),
        "pending_service_requests": await count(ServiceRequest, ServiceRequest.status == ServiceRequestStatus.SUBMITTED),
        "total_appointments": await count(Appointment),
        "pending_appointments": await count(Appointment, Appointment.status == AppointmentStatus.PENDING),
    }


@router.get("/community")
async def community_stats(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    async def count(model, *where):
        q = select(func.count(model.id))
        for w in where:
            q = q.where(w)
        return (await db.execute(q)).scalar_one()

    uid = current_user.id
    unread = await count(Notification, Notification.user_id == uid, Notification.is_read == False)  # noqa: E712

    return {
        "total_reports": await count(Report, Report.user_id == uid),
        "active_reports": await count(Report, Report.user_id == uid, Report.status.in_([ReportStatus.OPEN, ReportStatus.UNDER_REVIEW, ReportStatus.IN_PROGRESS])),
        "resolved_reports": await count(Report, Report.user_id == uid, Report.status == ReportStatus.RESOLVED),
        "total_service_requests": await count(ServiceRequest, ServiceRequest.user_id == uid),
        "active_service_requests": await count(ServiceRequest, ServiceRequest.user_id == uid, ServiceRequest.status.notin_([ServiceRequestStatus.COMPLETED, ServiceRequestStatus.REJECTED, ServiceRequestStatus.CANCELLED])),
        "total_appointments": await count(Appointment, Appointment.user_id == uid),
        "upcoming_appointments": await count(Appointment, Appointment.user_id == uid, Appointment.status.in_([AppointmentStatus.PENDING, AppointmentStatus.APPROVED])),
        "unread_notifications": unread,
    }


@router.get("/provider")
async def provider_stats(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    prov_result = await db.execute(select(Provider).where(Provider.user_id == current_user.id))
    provider = prov_result.scalar_one_or_none()
    if not provider:
        return {"error": "No provider profile found"}

    pid = provider.id

    async def count(model, *where):
        q = select(func.count(model.id))
        for w in where:
            q = q.where(w)
        return (await db.execute(q)).scalar_one()

    return {
        "total_service_requests": await count(ServiceRequest, ServiceRequest.provider_id == pid),
        "pending_service_requests": await count(ServiceRequest, ServiceRequest.provider_id == pid, ServiceRequest.status == ServiceRequestStatus.SUBMITTED),
        "in_progress_service_requests": await count(ServiceRequest, ServiceRequest.provider_id == pid, ServiceRequest.status == ServiceRequestStatus.IN_PROGRESS),
        "completed_service_requests": await count(ServiceRequest, ServiceRequest.provider_id == pid, ServiceRequest.status == ServiceRequestStatus.COMPLETED),
        "total_appointments": await count(Appointment, Appointment.provider_id == pid),
        "pending_appointments": await count(Appointment, Appointment.provider_id == pid, Appointment.status == AppointmentStatus.PENDING),
        "upcoming_appointments": await count(Appointment, Appointment.provider_id == pid, Appointment.status == AppointmentStatus.APPROVED),
        "reports_assigned": await count(Report, Report.provider_id == pid),
        "open_reports": await count(Report, Report.provider_id == pid, Report.status == ReportStatus.OPEN),
    }
