"""Appointment lifecycle tests."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.conftest import auth_header, make_provider, make_user
from app.models.user import UserRole


@pytest.mark.asyncio
async def test_book_and_approve_appointment(client: AsyncClient, db: AsyncSession):
    community = await make_user(db, email="community_appt@test.com", role=UserRole.COMMUNITY)
    prov_user = await make_user(db, email="prov_appt@test.com", role=UserRole.PROVIDER)
    provider = await make_provider(db, prov_user)

    # Book
    resp = await client.post("/api/v1/appointments", json={
        "provider_id": str(provider.id),
        "reason": "consultation",
        "meeting_type": "in_person",
        "appointment_date": "2026-06-15",
        "appointment_time": "10:00",
    }, headers=auth_header(community))
    assert resp.status_code == 201
    appt_id = resp.json()["id"]
    assert resp.json()["status"] == "pending"

    # Provider approves
    resp = await client.put(
        f"/api/v1/appointments/{appt_id}/status",
        json={"status": "approved"},
        headers=auth_header(prov_user),
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "approved"


@pytest.mark.asyncio
async def test_reschedule_flow(client: AsyncClient, db: AsyncSession):
    community = await make_user(db, email="community_resched@test.com", role=UserRole.COMMUNITY)
    prov_user = await make_user(db, email="prov_resched@test.com", role=UserRole.PROVIDER)
    provider = await make_provider(db, prov_user)

    # Book
    resp = await client.post("/api/v1/appointments", json={
        "provider_id": str(provider.id),
        "reason": "meter_reading",
        "meeting_type": "site_visit",
        "appointment_date": "2026-06-20",
        "appointment_time": "09:00",
    }, headers=auth_header(community))
    appt_id = resp.json()["id"]

    # User requests reschedule
    resp = await client.post(f"/api/v1/appointments/{appt_id}/reschedule-request", json={
        "requested_date": "2026-06-22",
        "requested_time": "14:00",
        "reschedule_reason": "Work conflict",
    }, headers=auth_header(community))
    assert resp.json()["status"] == "reschedule_requested"

    # Provider proposes alternative
    resp = await client.post(f"/api/v1/appointments/{appt_id}/provider-reschedule", json={
        "proposed_date": "2026-06-23",
        "proposed_time": "11:00",
        "proposed_message": "Monday works better",
    }, headers=auth_header(prov_user))
    assert resp.json()["status"] == "rescheduled"

    # User accepts
    resp = await client.post(f"/api/v1/appointments/{appt_id}/accept-reschedule", headers=auth_header(community))
    assert resp.json()["status"] == "approved"
    assert resp.json()["appointment_date"] == "2026-06-23"
