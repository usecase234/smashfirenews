"""jobs table

Revision ID: 954aad8a6fb0
Revises: 8f2a6c9d1b30
Create Date: 2026-09-07 14:15:20.399795

Phase 4 (docs/Smashfire_PR_Starting_Build_Plan.md): the queue infrastructure
that replaces the Phase 3 synchronous stub call. `jobs` carries publisher_id
per the Phase 1 tenancy hard rule, and idempotency_key (not globally unique
-- see app/db/models/jobs.py) is indexed since app/services/jobs.py's
idempotency check filters on it plus status on every enqueue call.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '954aad8a6fb0'
down_revision = '8f2a6c9d1b30'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "jobs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "publisher_id",
            sa.Integer(),
            sa.ForeignKey("publishers.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "submission_id",
            sa.Integer(),
            sa.ForeignKey("submissions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("action", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False, server_default="queued"),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("idempotency_key", sa.String(length=128), nullable=False),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_jobs_publisher_id", "jobs", ["publisher_id"])
    op.create_index("ix_jobs_submission_id", "jobs", ["submission_id"])
    op.create_index("ix_jobs_idempotency_key", "jobs", ["idempotency_key"])


def downgrade() -> None:
    op.drop_index("ix_jobs_idempotency_key", table_name="jobs")
    op.drop_index("ix_jobs_submission_id", table_name="jobs")
    op.drop_index("ix_jobs_publisher_id", table_name="jobs")
    op.drop_table("jobs")
