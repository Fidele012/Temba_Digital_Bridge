"""add_verification_workflow

Adds new status values to the three entity enums (resolution_submitted, verified,
closed_unverified, acknowledged, follow_up_required, management_review) and the
tracking columns needed for the provider-accountability / community-verification
workflow.

Revision ID: e3f4a5b6c7d8
Revises: d1e2f3a4b5c6
Create Date: 2026-06-03 12:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = 'e3f4a5b6c7d8'
down_revision: Union[str, None] = 'd1e2f3a4b5c6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# New values for each PostgreSQL enum type
_REPORT_NEW_VALUES = [
    'acknowledged', 'resolution_submitted', 'follow_up_required',
    'management_review', 'verified', 'closed_unverified',
]
_SR_NEW_VALUES = [
    'acknowledged', 'resolution_submitted', 'follow_up_required',
    'management_review', 'verified', 'closed_unverified',
]
_APPT_NEW_VALUES = [
    'resolution_submitted', 'verified', 'closed_unverified',
]


def upgrade() -> None:
    # ── Extend PostgreSQL enums (ADD VALUE is safe; cannot be rolled back easily) ──
    for v in _REPORT_NEW_VALUES:
        op.execute(f"ALTER TYPE reportstatus ADD VALUE IF NOT EXISTS '{v}'")
    for v in _SR_NEW_VALUES:
        op.execute(f"ALTER TYPE servicerequeststatus ADD VALUE IF NOT EXISTS '{v}'")
    for v in _APPT_NEW_VALUES:
        op.execute(f"ALTER TYPE appointmentstatus ADD VALUE IF NOT EXISTS '{v}'")

    # ── New tracking columns on reports ──
    op.add_column('reports', sa.Column('reopen_count', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('reports', sa.Column('first_responded_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('reports', sa.Column('resolution_submitted_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('reports', sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True))

    # ── New tracking columns on service_requests ──
    op.add_column('service_requests', sa.Column('reopen_count', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('service_requests', sa.Column('first_responded_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('service_requests', sa.Column('resolution_submitted_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('service_requests', sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True))

    # ── New tracking columns on appointments ──
    op.add_column('appointments', sa.Column('resolution_submitted_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('appointments', sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    # Note: PostgreSQL enum values cannot be removed without recreating the type.
    # Columns are dropped; enum values remain in the DB (harmless for rollback).
    for col in ('verified_at', 'resolution_submitted_at'):
        op.drop_column('appointments', col)

    for col in ('verified_at', 'resolution_submitted_at', 'first_responded_at', 'reopen_count'):
        op.drop_column('service_requests', col)
        op.drop_column('reports', col)
