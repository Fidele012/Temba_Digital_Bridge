# Temba Digital Bridge — Backend API

Production-grade REST API built with **FastAPI + PostgreSQL + Redis**.

---

## Stack

| Layer | Technology |
|-------|-----------|
| Framework | FastAPI 0.111 / Python 3.11 |
| Database | PostgreSQL 16 + SQLAlchemy 2 (async) |
| Migrations | Alembic |
| Auth | JWT (HS256) — 15-min access + 7-day refresh stored in Redis |
| Password | bcrypt via passlib |
| Cache / Rate-limit store | Redis 7 |
| Background tasks | Celery + Redis broker |
| SMS / USSD | Africa's Talking SDK |
| File storage | AWS S3 / MinIO |
| Email | SMTP + Jinja2 HTML templates |
| Monitoring | Sentry + structlog (JSON in prod) |
| Container | Docker + docker-compose |

---

## Quick Start (Docker)

```bash
# 1. Copy and fill in your secrets
cp .env.example .env

# 2. Launch everything (DB, Redis, MinIO, API, Celery)
docker compose up --build

# API is now at http://localhost:8000
# Swagger UI:  http://localhost:8000/docs
# Flower:      http://localhost:5555
# MinIO:       http://localhost:9001
```

---

## Local Development (no Docker)

```bash
# Prerequisites: Python 3.11+, PostgreSQL, Redis

python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/macOS

pip install -r requirements.txt
cp .env.example .env
# Edit .env — fill in DATABASE_URL, SECRET_KEY etc.

# Run migrations
alembic upgrade head

# Start API
uvicorn app.main:app --reload --port 8000

# Start Celery worker (separate terminal)
celery -A app.worker worker --loglevel=info
```

---

## API Structure

```
/api/v1/
├── auth/           register, login, refresh, logout, forgot/reset password
├── users/          profile management, admin CRUD
├── providers/      registration, availability, admin approval
├── reports/        create, list, update status, attach media
├── service-requests/  create, list, update status, cancel
├── appointments/   book, reschedule, approve/reject/complete
├── notifications/  list, mark-read, announcements
├── analytics/      overview (admin), community stats, provider stats
└── ussd/           Africa's Talking USSD callback
```

---

## Security

- **JWT RBAC** — three roles: `community`, `provider`, `admin`
- **bcrypt** — cost factor 12 (passlib default)
- **Refresh tokens** stored in Redis; invalidated on logout / password change
- **Rate limiting** — 60 req/min global, 10 req/min on auth endpoints (slowapi)
- **Security headers** — `X-Content-Type-Options`, `X-Frame-Options`, `HSTS` (prod), etc.
- **CORS** — explicit origin allowlist
- **Audit logging** — every mutating action writes to `audit_logs` table
- **SQL injection** — prevented by SQLAlchemy ORM (no raw SQL)
- **Input validation** — Pydantic v2 with strict field validators (password strength, regex patterns)
- **File upload** — MIME type allowlist + size cap (configurable `MAX_FILE_SIZE_MB`)

---

## Environment Variables

See [.env.example](.env.example) for the full list with descriptions.

**Required for production:**

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | 64-char random string — generate with `openssl rand -hex 32` |
| `DATABASE_URL` | `postgresql+asyncpg://user:pass@host/db` |
| `DATABASE_URL_SYNC` | `postgresql://user:pass@host/db` (for Alembic) |
| `REDIS_URL` | `redis://host:6379/0` |
| `ENVIRONMENT` | `production` |

---

## Running Tests

```bash
pip install -r requirements.txt
pytest --cov=app --cov-report=term-missing
```

Tests use an **in-memory SQLite** database (no external services needed).

---

## Deployment Checklist

- [ ] `SECRET_KEY` changed to a cryptographically random value
- [ ] `ENVIRONMENT=production`
- [ ] `DEBUG=false`
- [ ] `FIRST_ADMIN_PASSWORD` changed
- [ ] `ALLOWED_HOSTS` and `CORS_ORIGINS` set to production domains
- [ ] HTTPS configured (Nginx/Caddy reverse proxy)
- [ ] `SENTRY_DSN` set for error tracking
- [ ] DB and Redis running on private network
- [ ] `MAX_FILE_SIZE_MB` reviewed
- [ ] AT credentials set for live SMS/USSD
