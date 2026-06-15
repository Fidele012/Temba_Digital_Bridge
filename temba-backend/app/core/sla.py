"""SLA deadline configuration and helpers for reports, appointments, and service requests."""
from datetime import datetime, timedelta, timezone

_REPORT_SLA_H: dict[str, int] = {
    "contamination": 48,
    "pipe_burst": 168,
    "low_pressure": 72,
    "no_supply": 72,
    "water_quality": 72,
    "billing": 120,
    "meter": 120,
    "other": 120,
}

_APPOINTMENT_SLA_H: dict[str, int] = {
    "water_connection": 336,
    "meter_reading": 120,
    "pipe_repair": 168,
    "consultation": 120,
    "inspection": 72,
    "billing": 120,
    "other": 120,
}

_SERVICE_REQUEST_SLA_H: dict[str, int] = {
    "water_connection": 336,
    "tank_delivery": 48,
    "truck_delivery": 48,
    "meter_support": 120,
    "inspection": 72,
}

_DEFAULT_SLA_H = 120


def sla_deadline_for(category: str, created_at: datetime, item_type: str = "report") -> datetime:
    """Return the SLA deadline for a given category and creation timestamp."""
    if item_type == "appointment":
        hours = _APPOINTMENT_SLA_H.get(category, _DEFAULT_SLA_H)
    elif item_type == "service_request":
        hours = _SERVICE_REQUEST_SLA_H.get(category, _DEFAULT_SLA_H)
    else:
        hours = _REPORT_SLA_H.get(category, _DEFAULT_SLA_H)

    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)

    return created_at + timedelta(hours=hours)
