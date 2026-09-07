"""
Async job queue bookkeeping (Phase 4, docs/Smashfire_PR_Starting_Build_Plan.md).

One row per enqueued constrained AI action. This table is the DB-side
source of truth the job-status endpoint (app/api/jobs.py) reads from; the
arq worker (app/workers/worker.py) is the only thing that ever moves a row
through queued -> running -> succeeded | failed | dead, and
app/services/jobs.py is the only place that writes to it -- mirrors how
draft_versions has one service (app/services/drafts.py) as its single
writer.

TenantScopedMixin per the hard rule that every Hub table carries
publisher_id from its first migration.
"""
from __future__ import annotations

import datetime as dt

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.tenancy import TenantScopedMixin


class Job(Base, TenantScopedMixin):
    """One enqueued run of a constrained AI action against one submission."""

    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    submission_id: Mapped[int] = mapped_column(
        ForeignKey("submissions.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # One of the five constrained actions named in CLAUDE.md's hard rules --
    # never a free-form prompt. app/workers/worker.py looks up the handler
    # to run from this string via its ACTION_HANDLERS table.
    action: Mapped[str] = mapped_column(String(64))

    # queued -> running -> succeeded | failed | dead. See
    # app/services/jobs.py for the transitions.
    status: Mapped[str] = mapped_column(String(16), default="queued", server_default="queued")
    attempts: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    # f"{action}:{submission_id}" -- lets a second enqueue call for the same
    # action+submission find and return the still-active job instead of
    # creating a duplicate (the Phase 4 idempotency requirement). Not
    # globally unique: once a job reaches a terminal status, the same key
    # is free to be reused by a later, separate job -- e.g. a second
    # generate-draft call made after the first one already finished.
    idempotency_key: Mapped[str] = mapped_column(String(128), index=True)

    error: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: dt.datetime.now(dt.timezone.utc)
    )
    started_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
