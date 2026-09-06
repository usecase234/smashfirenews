"""
Tenant/Publisher model and the per-installation credential that maps a
WordPress plugin install to exactly one publisher_id.

Buddy Magazine is Publisher/Tenant #001 — see
docs/Smashfire_PR_Full_Product_Technical_Plan_2026.md and
scripts/seed_buddy_magazine.py.
"""
from __future__ import annotations

import datetime as dt

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Publisher(Base):
    """A tenant. Not itself tenant-scoped — this is the scope root."""

    __tablename__ = "publishers"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(32), default="active", server_default="active")
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: dt.datetime.now(dt.timezone.utc)
    )

    installations: Mapped[list["PublisherInstallation"]] = relationship(
        back_populates="publisher", cascade="all, delete-orphan"
    )


class PublisherInstallation(Base):
    """One WordPress plugin install's credential -> publisher_id mapping.

    This is the "WP installation secret" from the Hub credential separation
    table in the source plan: it authenticates plugin<->Hub requests and
    resolves a tenant, and it is never an LLM provider key. The plaintext
    token is shown to the installer exactly once (at issue time); only its
    hash is ever persisted.
    """

    __tablename__ = "publisher_installations"

    id: Mapped[int] = mapped_column(primary_key=True)
    publisher_id: Mapped[int] = mapped_column(
        ForeignKey("publishers.id", ondelete="CASCADE"), nullable=False, index=True
    )
    site_id: Mapped[str] = mapped_column(String(128))
    site_url: Mapped[str] = mapped_column(String(512))
    credential_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    plugin_version: Mapped[str | None] = mapped_column(String(32), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="active", server_default="active")
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: dt.datetime.now(dt.timezone.utc)
    )
    last_seen_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    publisher: Mapped["Publisher"] = relationship(back_populates="installations")
