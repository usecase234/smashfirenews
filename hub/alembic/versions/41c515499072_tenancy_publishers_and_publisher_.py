"""tenancy: publishers and publisher_installations

Revision ID: 41c515499072
Revises:
Create Date: 2026-09-06 13:31:32.259700

Phase 1 (docs/Smashfire_PR_Starting_Build_Plan.md): the tenancy skeleton.
`publishers` is the scope root every other table's publisher_id FKs into.
`publisher_installations` maps a WordPress plugin install's credential hash
to exactly one publisher_id — this is the "WP installation secret" from the
Hub credential separation table in the source plan, never an LLM key.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '41c515499072'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "publishers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("slug", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index("ix_publishers_slug", "publishers", ["slug"], unique=True)

    op.create_table(
        "publisher_installations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "publisher_id",
            sa.Integer(),
            sa.ForeignKey("publishers.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("site_id", sa.String(length=128), nullable=False),
        sa.Column("site_url", sa.String(length=512), nullable=False),
        sa.Column("credential_hash", sa.String(length=64), nullable=False),
        sa.Column("plugin_version", sa.String(length=32), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "ix_publisher_installations_publisher_id",
        "publisher_installations",
        ["publisher_id"],
    )
    op.create_index(
        "ix_publisher_installations_credential_hash",
        "publisher_installations",
        ["credential_hash"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("ix_publisher_installations_credential_hash", table_name="publisher_installations")
    op.drop_index("ix_publisher_installations_publisher_id", table_name="publisher_installations")
    op.drop_table("publisher_installations")
    op.drop_index("ix_publishers_slug", table_name="publishers")
    op.drop_table("publishers")
