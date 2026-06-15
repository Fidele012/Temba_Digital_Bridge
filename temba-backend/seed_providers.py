"""
Seed the database with Temba's real water provider accounts.
Run: .venv\Scripts\python.exe seed_providers.py

Idempotent — safe to run multiple times.
"""
import asyncio
import sys

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# ── Config ─────────────────────────────────────────────────────────────────────
import os
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://temba:temba_pass@localhost:5432/temba_db",
)

_PROVIDERS = [
    {
        "email":             "info@wasac.rw",
        "full_name":         "WASAC Administrator",
        "organization_name": "WASAC",
        "description":       "Water and Sanitation Corporation — Rwanda's national water utility.",
        "phone":             "+250788123456",
        "org_phone":         "+250788123456",
        "org_email":         "info@wasac.rw",
        "website":           "https://www.wasac.rw",
        "service_categories": ["water_supply", "sanitation", "infrastructure"],
        "provinces":         ["Kigali City", "Northern Province", "Southern Province",
                              "Eastern Province", "Western Province"],
    },
    {
        "email":             "support@iriba.rw",
        "full_name":         "IRIBA Water Group Admin",
        "organization_name": "IRIBA Water Group",
        "description":       "Urban water distribution specialist serving Kigali and peri-urban areas.",
        "phone":             "+250788345678",
        "org_phone":         "+250788345678",
        "org_email":         "support@iriba.rw",
        "website":           None,
        "service_categories": ["water_supply", "meter_services", "water_quality"],
        "provinces":         ["Kigali City"],
    },
    {
        "email":             "hello@prowater.rw",
        "full_name":         "Pro Water Rwanda Admin",
        "organization_name": "Pro Water Rwanda",
        "description":       "Commercial water supply and water truck delivery across Rwanda.",
        "phone":             "+250788567890",
        "org_phone":         "+250788567890",
        "org_email":         "hello@prowater.rw",
        "website":           None,
        "service_categories": ["truck_delivery", "water_storage", "water_supply"],
        "provinces":         ["Kigali City", "Eastern Province", "Southern Province"],
    },
]

# ── Bootstrap imports after setting up path ────────────────────────────────────
sys.path.insert(0, ".")

# Import ALL models so SQLAlchemy can resolve cross-model relationships
import app.models.user            # noqa: F401
import app.models.provider        # noqa: F401
import app.models.report          # noqa: F401
import app.models.service_request # noqa: F401
import app.models.appointment     # noqa: F401
import app.models.notification    # noqa: F401

from app.core.security import hash_password
from app.models.provider import Provider, ProviderServiceArea, ProviderStatus
from app.models.user import User, UserRole


async def seed(db: AsyncSession) -> None:
    created = 0
    skipped = 0

    for p in _PROVIDERS:
        # Check if this provider already exists by email
        existing_user = (await db.execute(
            select(User).where(User.email == p["email"])
        )).scalar_one_or_none()

        if existing_user:
            # Check provider profile exists
            existing_prov = (await db.execute(
                select(Provider).where(Provider.user_id == existing_user.id)
            )).scalar_one_or_none()
            if existing_prov:
                print(f"  SKIP  {p['organization_name']} (already in DB, id={str(existing_prov.id)[:8]})")
                skipped += 1
                continue
            # User exists but no provider profile — create the profile
            user = existing_user
        else:
            # Check if phone is already taken by another account
            phone_conflict = (await db.execute(
                select(User).where(User.phone == p["phone"])
            )).scalar_one_or_none()
            # Use None if phone is already taken (provider will use email-based login)
            phone = None if phone_conflict else p["phone"]

            # Create provider user account
            user = User(
                email=p["email"],
                phone=phone,
                full_name=p["full_name"],
                hashed_password=hash_password("Temba@Provider2025!"),
                role=UserRole.PROVIDER,
                is_active=True,
                is_verified=True,
            )
            db.add(user)
            await db.flush()

        # Create provider profile — status APPROVED so USSD can see them
        provider = Provider(
            user_id=user.id,
            organization_name=p["organization_name"],
            description=p["description"],
            phone=p["org_phone"],
            email=p["org_email"],
            website=p["website"],
            service_categories=p["service_categories"],
            custom_services=[],
            status=ProviderStatus.APPROVED,
            working_days=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
            work_start_time="08:00",
            work_end_time="17:00",
            max_appointments_per_day=20,
            unavailable_dates=[],
        )
        db.add(provider)
        await db.flush()

        # Add service areas (one row per province)
        for province in p["provinces"]:
            db.add(ProviderServiceArea(
                provider_id=provider.id,
                province=province,
            ))

        print(f"  CREATE {p['organization_name']} → user {str(user.id)[:8]}  provider {str(provider.id)[:8]}")
        created += 1

    await db.commit()
    print(f"\nDone — {created} created, {skipped} skipped.")


async def main() -> None:
    print("\nTemba Provider Seed")
    engine = create_async_engine(DATABASE_URL, echo=False)
    factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as db:
        await seed(db)
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
