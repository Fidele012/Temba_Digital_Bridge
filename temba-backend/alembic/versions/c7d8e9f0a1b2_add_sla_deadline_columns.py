"""add_sla_deadline_columns

Revision ID: c7d8e9f0a1b2
Revises: 9ef9f71f4d78
Create Date: 2026-06-03 10:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = 'c7d8e9f0a1b2'
down_revision: Union[str, None] = '9ef9f71f4d78'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('reports', sa.Column('sla_deadline', sa.DateTime(timezone=True), nullable=True))
    op.add_column('reports', sa.Column('overdue_flagged', sa.Boolean(), nullable=False, server_default=sa.false()))

    op.add_column('appointments', sa.Column('sla_deadline', sa.DateTime(timezone=True), nullable=True))
    op.add_column('appointments', sa.Column('overdue_flagged', sa.Boolean(), nullable=False, server_default=sa.false()))

    op.add_column('service_requests', sa.Column('sla_deadline', sa.DateTime(timezone=True), nullable=True))
    op.add_column('service_requests', sa.Column('overdue_flagged', sa.Boolean(), nullable=False, server_default=sa.false()))


def downgrade() -> None:
    op.drop_column('service_requests', 'overdue_flagged')
    op.drop_column('service_requests', 'sla_deadline')
    op.drop_column('appointments', 'overdue_flagged')
    op.drop_column('appointments', 'sla_deadline')
    op.drop_column('reports', 'overdue_flagged')
    op.drop_column('reports', 'sla_deadline')
