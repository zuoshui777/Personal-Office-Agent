"""baseline database schema

Revision ID: 20260804_baseline
Revises:
Create Date: 2026-08-04
"""

from alembic import op

from app.database.connection import Base


revision = "20260804_baseline"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)


def downgrade() -> None:
    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind)
