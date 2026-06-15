"""Report endpoint tests."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.conftest import auth_header, make_user
from app.models.user import UserRole

_REPORT_PAYLOAD = {
    "category": "pipe_burst",
    "urgency": "high",
    "title": "Burst pipe on Kigali Ave",
    "description": "Water is flooding the road near sector office",
    "province": "Kigali City",
    "district": "Nyarugenge",
}


@pytest.mark.asyncio
async def test_create_report(client: AsyncClient, db: AsyncSession):
    user = await make_user(db, email="reporter@test.com")
    resp = await client.post("/api/v1/reports", json=_REPORT_PAYLOAD, headers=auth_header(user))
    assert resp.status_code == 201
    data = resp.json()
    assert data["category"] == "pipe_burst"
    assert data["status"] == "open"


@pytest.mark.asyncio
async def test_list_reports_community_only_sees_own(client: AsyncClient, db: AsyncSession):
    u1 = await make_user(db, email="u1@test.com")
    u2 = await make_user(db, email="u2@test.com")

    await client.post("/api/v1/reports", json=_REPORT_PAYLOAD, headers=auth_header(u1))
    await client.post("/api/v1/reports", json=_REPORT_PAYLOAD | {"title": "Another"}, headers=auth_header(u2))

    resp = await client.get("/api/v1/reports", headers=auth_header(u1))
    assert resp.status_code == 200
    for r in resp.json()["items"]:
        assert r["user_id"] == str(u1.id)


@pytest.mark.asyncio
async def test_get_report_forbidden_for_other_user(client: AsyncClient, db: AsyncSession):
    owner = await make_user(db, email="owner@test.com")
    other = await make_user(db, email="other@test.com")

    create_resp = await client.post("/api/v1/reports", json=_REPORT_PAYLOAD, headers=auth_header(owner))
    report_id = create_resp.json()["id"]

    resp = await client.get(f"/api/v1/reports/{report_id}", headers=auth_header(other))
    assert resp.status_code == 403
