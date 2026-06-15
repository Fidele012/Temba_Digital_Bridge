"""
Public issue tracking endpoint — no authentication required.
GET /track/{ref}  → look up a report or service request by its reference number
                    Returns only status/progress info, no personal data.
"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.models.report import Report
from app.models.service_request import ServiceRequest

router = APIRouter(prefix="/track", tags=["track"])

_REPORT_STATUS_LABEL = {
    "open":                   {"en": "Submitted - awaiting review",        "rw": "Yoherejwe - irategerezwa"},
    "acknowledged":           {"en": "Acknowledged by provider",           "rw": "Yemejwe n'umutanga serivisi"},
    "under_review":           {"en": "Under review",                       "rw": "Irasuzumwa"},
    "in_progress":            {"en": "In progress",                        "rw": "Irakozwe"},
    "resolution_submitted":   {"en": "Solution submitted - awaiting confirmation", "rw": "Igisubizo cyatanzwe - turetse kwemeza kwawe"},
    "follow_up_required":     {"en": "Follow-up required",                 "rw": "Hakenewe kongera gufatana na we"},
    "management_review":      {"en": "Under management review",            "rw": "Irasuzumwa n'ubuyobozi"},
    "verified":               {"en": "Resolved and verified",              "rw": "Byakemuwe kandi byemejwe"},
    "closed_unverified":      {"en": "Closed (unverified)",                "rw": "Bifunzwe (bitaremejwe)"},
    "resolved":               {"en": "Resolved",                           "rw": "Byakemuwe"},
    "closed":                 {"en": "Closed",                             "rw": "Bifunzwe"},
}

_SVC_STATUS_LABEL = {
    "submitted":              {"en": "Submitted - awaiting review",        "rw": "Yoherejwe - irategerezwa"},
    "acknowledged":           {"en": "Acknowledged by provider",           "rw": "Yemejwe n'umutanga serivisi"},
    "reviewing":              {"en": "Under review",                       "rw": "Irasuzumwa"},
    "approved":               {"en": "Approved",                           "rw": "Yemejwe"},
    "in_progress":            {"en": "In progress",                        "rw": "Irakozwe"},
    "resolution_submitted":   {"en": "Work completed - awaiting confirmation", "rw": "Akazi karangiye - turetse kwemeza kwawe"},
    "follow_up_required":     {"en": "Follow-up required",                 "rw": "Hakenewe kongera gufatana na we"},
    "management_review":      {"en": "Under management review",            "rw": "Irasuzumwa n'ubuyobozi"},
    "verified":               {"en": "Completed and verified",             "rw": "Byakozwe kandi byemejwe"},
    "closed_unverified":      {"en": "Closed (unverified)",                "rw": "Bifunzwe (bitaremejwe)"},
    "completed":              {"en": "Completed",                          "rw": "Byarangiye"},
    "rejected":               {"en": "Rejected",                           "rw": "Byanzwe"},
    "cancelled":              {"en": "Cancelled",                          "rw": "Byahagaritswe"},
}

_URGENCY_LABEL = {
    "low":      {"en": "Low",      "rw": "Ntabwoba"},
    "medium":   {"en": "Medium",   "rw": "Hagati"},
    "high":     {"en": "High",     "rw": "Byihutirwa"},
    "critical": {"en": "Critical", "rw": "Bikomeye cyane"},
}

_CAT_LABEL = {
    "contamination":  {"en": "Water Contamination", "rw": "Amazi yarenzwe"},
    "pipe_burst":     {"en": "Pipe Burst / Leak",   "rw": "Inkweto yatuye"},
    "low_pressure":   {"en": "Low Water Pressure",  "rw": "Ingufu z'amazi nke"},
    "no_supply":      {"en": "No Water Supply",     "rw": "Nta mazi"},
    "water_quality":  {"en": "Water Quality",       "rw": "Ubwiza bw'amazi"},
    "billing":        {"en": "Billing Issue",       "rw": "Ikibazo cy'ishyurwa"},
    "meter":          {"en": "Meter Issue",         "rw": "Ikibazo cya konteri"},
    "other":          {"en": "Other",               "rw": "Ikindi"},
}

_SVC_TYPE_LABEL = {
    "water_connection": {"en": "New Water Connection", "rw": "Guhuza amazi mashya"},
    "tank_delivery":    {"en": "Water Tank Delivery",  "rw": "Gutanga isereri ry'amazi"},
    "truck_delivery":   {"en": "Water Truck Delivery", "rw": "Gutanga amazi na camion"},
    "meter_support":    {"en": "Meter Support",        "rw": "Serivisi ya konteri"},
    "inspection":       {"en": "Technical Inspection", "rw": "Igenzura ry'imyitozo"},
}


class TrackResult(BaseModel):
    reference_number: str
    type: str            # "report" | "service_request"
    category: str        # human-readable category / service type
    category_rw: str
    status: str          # human-readable status label
    status_rw: str
    urgency: str
    urgency_rw: str
    provider: str | None
    location: str | None
    submitted_at: str    # ISO date string
    resolution_notes: str | None


@router.get("/{ref}", response_model=TrackResult)
async def track_issue(
    ref: str,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TrackResult:
    ref = ref.strip().upper()

    # ── Try reports first ─────────────────────────────────────────────────────
    r_row = (await db.execute(
        select(Report)
        .where(Report.reference_number == ref)
        .options(selectinload(Report.provider))
    )).scalar_one_or_none()

    if r_row:
        status_val = r_row.status.value if hasattr(r_row.status, "value") else str(r_row.status)
        urg_val = r_row.urgency.value if hasattr(r_row.urgency, "value") else str(r_row.urgency)
        cat_val = r_row.category.value if hasattr(r_row.category, "value") else str(r_row.category)
        sl = _REPORT_STATUS_LABEL.get(status_val, {"en": status_val, "rw": status_val})
        ul = _URGENCY_LABEL.get(urg_val, {"en": urg_val, "rw": urg_val})
        cl = _CAT_LABEL.get(cat_val, {"en": cat_val, "rw": cat_val})
        loc_parts = [p for p in [r_row.sector, r_row.district, r_row.province] if p]
        return TrackResult(
            reference_number=ref,
            type="report",
            category=cl["en"],
            category_rw=cl["rw"],
            status=sl["en"],
            status_rw=sl["rw"],
            urgency=ul["en"],
            urgency_rw=ul["rw"],
            provider=r_row.provider.organization_name if r_row.provider else None,
            location=", ".join(loc_parts) if loc_parts else None,
            submitted_at=r_row.created_at.strftime("%Y-%m-%d"),
            resolution_notes=r_row.resolution_notes,
        )

    # ── Try service requests ──────────────────────────────────────────────────
    s_row = (await db.execute(
        select(ServiceRequest)
        .where(ServiceRequest.reference_number == ref)
        .options(selectinload(ServiceRequest.provider))
    )).scalar_one_or_none()

    if s_row:
        status_val = s_row.status.value if hasattr(s_row.status, "value") else str(s_row.status)
        urg_val = s_row.urgency.value if hasattr(s_row.urgency, "value") else str(s_row.urgency)
        svc_val = s_row.request_type.value if hasattr(s_row.request_type, "value") else str(s_row.request_type)
        sl = _SVC_STATUS_LABEL.get(status_val, {"en": status_val, "rw": status_val})
        ul = _URGENCY_LABEL.get(urg_val, {"en": urg_val, "rw": urg_val})
        tl = _SVC_TYPE_LABEL.get(svc_val, {"en": svc_val, "rw": svc_val})
        loc_parts = [p for p in [s_row.sector, s_row.district, s_row.province] if p]
        return TrackResult(
            reference_number=ref,
            type="service_request",
            category=tl["en"],
            category_rw=tl["rw"],
            status=sl["en"],
            status_rw=sl["rw"],
            urgency=ul["en"],
            urgency_rw=ul["rw"],
            provider=s_row.provider.organization_name if s_row.provider else None,
            location=", ".join(loc_parts) if loc_parts else None,
            submitted_at=s_row.created_at.strftime("%Y-%m-%d"),
            resolution_notes=s_row.provider_notes,
        )

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="No issue found with that tracking code.",
    )
