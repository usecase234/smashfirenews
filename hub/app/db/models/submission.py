"""
Phase 3 vertical slice: Submission (immutable original) and DraftVersion
(versioned editorial derivative).

Both are TenantScopedMixin tables per the hard rule that every Hub table
carries publisher_id from its first migration — DraftVersion included, even
though it hangs off Submission, so a query for one tenant's drafts never has
to join through Submission to be safely scoped.

`Submission.body_text` is never modified after creation. Draft generation
(app/services/drafts.py) only ever inserts a new DraftVersion row — see
docs/Smashfire_PR_Full_Product_Technical_Plan_2026.md, "Rights & provenance"
and the CLAUDE.md hard rule on immutable originals / versioned derivatives.
"""
from __future__ import annotations

import datetime as dt

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.tenancy import TenantScopedMixin


class Submission(Base, TenantScopedMixin):
    """The publicist's original release. Immutable once created."""

    __tablename__ = "submissions"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Immutable original content.
    headline: Mapped[str] = mapped_column(String(512))
    body_text: Mapped[str] = mapped_column(Text)

    # Submitter identity, captured at intake time.
    sender_name: Mapped[str] = mapped_column(String(255))
    sender_email: Mapped[str] = mapped_column(String(255))
    sender_company: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # queued -> drafted -> published (or rejected/archived), see
    # app/services/submissions.py for the transitions.
    status: Mapped[str] = mapped_column(String(32), default="queued", server_default="queued")

    # Provenance recorded once the plugin has actually created the WordPress
    # post — the Hub never creates that post itself. Kept private per the
    # doc's "retains source provenance privately."
    wp_post_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    live_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    published_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: dt.datetime.now(dt.timezone.utc)
    )

    drafts: Mapped[list["DraftVersion"]] = relationship(
        back_populates="submission", cascade="all, delete-orphan", order_by="DraftVersion.version"
    )


class DraftVersion(Base, TenantScopedMixin):
    """One versioned editorial derivative of a Submission. Never overwritten."""

    __tablename__ = "draft_versions"
    __table_args__ = (UniqueConstraint("submission_id", "version", name="uq_draft_versions_submission_version"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    submission_id: Mapped[int] = mapped_column(
        ForeignKey("submissions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    version: Mapped[int] = mapped_column(Integer)
    body_text: Mapped[str] = mapped_column(Text)

    # e.g. "stub-v1" for the Phase 3 echo stub; a real model id from Phase 4
    # on. Never a free-form prompt — see the hard rule against passthrough.
    generator: Mapped[str] = mapped_column(String(64))

    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: dt.datetime.now(dt.timezone.utc)
    )

    submission: Mapped["Submission"] = relationship(back_populates="drafts")
