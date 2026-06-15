"""
Pytest fixtures providing:
- An in-memory SQLite async engine (no Postgres needed for unit tests)
- A test client that overrides the DB and Redis dependencies
- Factory helpers for users, providers, reports, appointments
"""
import asyncio
from collections.abc import AsyncGenerator
from typing import Any

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.security import create_access_token, hash_password
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.appointment import Appointment, AppointmentReason, AppointmentStatus, MeetingType
from app.models.provider import Provider, ProviderStatus
from app.models.report import Report, ReportCategory, ReportStatus, ReportUrgency
from app.models.user import User, UserRole

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(TEST_DB_URL, echo=False)
TestSession = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db() -> AsyncGenerator[AsyncSession, None]:
    async with TestSession() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    app.dependency_overrides[get_db] = lambda: db
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


# ── User factory ──────────────────────────────────────────────────────────────

async def make_user(db: AsyncSession, role: UserRole = UserRole.COMMUNITY, **kwargs) -> User:
    defaults: dict[str, Any] = {
        "email": f"user_{role.value}_{id(kwargs)}@test.com",
        "hashed_password": hash_password("Test@12345"),
        "full_name": f"Test {role.value.capitalize()}",
        "role": role,
        "is_active": True,
        "is_verified": True,
    }
    defaults.update(kwargs)
    user = User(**defaults)
    db.add(user)
    await db.flush()
    return user


def auth_header(user: User) -> dict[str, str]:
    token = create_access_token(user.id, user.role.value)
    return {"Authorization": f"Bearer {token}"}


# ── Provider factory ──────────────────────────────────────────────────────────

async def make_provider(db: AsyncSession, user: User, **kwargs) -> Provider:
    defaults: dict[str, Any] = {
        "user_id": user.id,
        "organization_name": "Test Water Co",
        "status": ProviderStatus.APPROVED,
        "service_categories": ["water_supply"],
        "custom_services": [],
        "working_days": ["monday", "tuesday", "wednesday", "thursday", "friday"],
        "max_appointments_per_day": 10,
        "unavailable_dates": [],
    }
    defaults.update(kwargs)
    provider = Provider(**defaults)
    db.add(provider)
    await db.flush()
    return provider
