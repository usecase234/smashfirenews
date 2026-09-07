"""submissions and draft_versions

Revision ID: 8f2a6c9d1b30
Revises: 41c515499072
Create Date: 2026-09-06 15:00:00.000000

Phase 3 (docs/Smashfire_PR_Starting_Build_Plan.md): the thin vertical slice.
`submissions` holds the publicist's immutable original; `draft_versions`
holds versioned editorial derivatives (Draft V1, V2, ...) that are only ever
inserted, never updated in place. Both carry publisher_id per the tenancy
hard rule established in Phase 1.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8f2a6c9d1b30'
down_revision = '41c515499072'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "submissions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "publisher_id",
            sa.Integer(),
            sa.ForeignKey("publishers.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("headline", sa.String(length=512), nullable=False),
        sa.Column("body_text", sa.Text(), nullable=False),
        sa.Column("sender_name", sa.String(length=255), nullable=False),
        sa.Column("sender_email", sa.String(length=255), nullable=False),
        sa.Column("sender_company", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="queued"),
        sa.Column("wp_post_id", sa.Integer(), nullable=True),
        sa.Column("live_url", sa.String(length=1024), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index("ix_submissions_publisher_id", "submissions", ["publisher_id"])

    op.create_table(
        "draft_versions",
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
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("body_text", sa.Text(), nullable=False),
        sa.Column("generator", sa.String(length=64), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.UniqueConstraint("submission_id", "version", name="uq_draft_versions_submission_version"),
    )
    op.create_index("ix_draft_versions_publisher_id", "draft_versions", ["publisher_id"])
    op.create_index("ix_draft_versions_submission_id", "draft_versions", ["submission_id"])


def downgrade() -> None:
    op.drop_index("ix_draft_versions_submission_id", table_name="draft_versions")
    op.drop_index("ix_draft_versions_publisher_id", table_name="draft_versions")
    op.drop_table("draft_versions")
    op.drop_index("ix_submissions_publisher_id", table_name="submissions")
    op.drop_table("submissions")
