"""Add reference_number to reports and service_requests

Revision ID: f1e2d3c4b5a6
Revises: d1e2f3a4b5c6
Create Date: 2026-06-12 00:00:00.000000
"""
from typing import Union

import sqlalchemy as sa
from alembic import op

revision: str = "f1e2d3c4b5a6"
down_revision: Union[str, None] = "e3f4a5b6c7d8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("reports", sa.Column("reference_number", sa.String(20), nullable=True))
    op.create_unique_constraint("uq_reports_reference_number", "reports", ["reference_number"])
    op.create_index("ix_reports_reference_number", "reports", ["reference_number"])

    op.add_column("service_requests", sa.Column("reference_number", sa.String(20), nullable=True))
    op.create_unique_constraint("uq_svc_requests_reference_number", "service_requests", ["reference_number"])
    op.create_index("ix_svc_requests_reference_number", "service_requests", ["reference_number"])


def downgrade() -> None:
    op.drop_index("ix_svc_requests_reference_number", table_name="service_requests")
    op.drop_constraint("uq_svc_requests_reference_number", "service_requests", type_="unique")
    op.drop_column("service_requests", "reference_number")

    op.drop_index("ix_reports_reference_number", table_name="reports")
    op.drop_constraint("uq_reports_reference_number", "reports", type_="unique")
    op.drop_column("reports", "reference_number")
