"""
Job queue bookkeeping: the DB-side source of truth for async AI actions.

Phase 4 (docs/Smashfire_PR_Starting_Build_Plan.md) replaces the Phase 3
synchronous stub call with a queued job the arq worker (app/workers/worker.py)
picks up. This module only ever touches the `jobs` table -- the actual
Redis enqueue happens in the API route (app/api/submissions.py), right
after a job is confirmed new, so a job never exists in Redis without first
existing here.

Every read goes through `tenant_scoped_select`, same as
app/services/submissions.py, so a job can never be fetched or acted on
outside the tenant that owns it.
"""
from __future__ import annotations

import datetime as dt

from sqlalchemy.orm import Session

from app.db.models.jobs import Job
from app.db.tenancy import tenant_scoped_select

# A job in either of these statuses is still "active" -- a second enqueue
# call for the same action+submission must return it rather than create a
# duplicate. Once a job leaves this set (succeeded/failed/dead) its
# idempotency_key is free to be reused by a later, separate job.
ACTIVE_STATUSES = ("queued", "running")

# Matched by app/workers/worker.py's arq `max_tries` so arq's own retry
# ceiling and this module's failed-vs-dead decision never disagree.
MAX_ATTEMPTS = 3


def get_or_create_job(db: Session, publisher_id: int, submission_id: int, action: str) -> tuple[Job, bool]:
    """Returns (job, created).

    If a queued/running job already exists for this exact action+submission,
    returns it unchanged -- the Phase 4 idempotency requirement. Otherwise
    inserts a new queued job.
    """
    idempotency_key = f"{action}:{submission_id}"
    existing = db.scalars(
        tenant_scoped_select(Job, publisher_id).where(
            Job.idempotency_key == idempotency_key,
            Job.status.in_(ACTIVE_STATUSES),
        )
    ).first()
    if existing is not None:
        return existing, False

    job = Job(
        publisher_id=publisher_id,
        submission_id=submission_id,
        action=action,
        idempotency_key=idempotency_key,
        status="queued",
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job, True


def get_job(db: Session, publisher_id: int, job_id: int) -> Job | None:
    return db.scalars(tenant_scoped_select(Job, publisher_id).where(Job.id == job_id)).one_or_none()


def mark_running(db: Session, job: Job) -> None:
    job.status = "running"
    job.attempts += 1
    if job.started_at is None:
        job.started_at = dt.datetime.now(dt.timezone.utc)
    db.commit()
    db.refresh(job)


def mark_succeeded(db: Session, job: Job) -> None:
    job.status = "succeeded"
    job.finished_at = dt.datetime.now(dt.timezone.utc)
    job.error = None
    db.commit()
    db.refresh(job)


def mark_failed(db: Session, job: Job, error: str) -> None:
    """A run of the job errored. `attempts` (bumped by mark_running) decides
    whether this is a retryable failure or the dead-letter end of the line."""
    job.status = "dead" if job.attempts >= MAX_ATTEMPTS else "failed"
    job.finished_at = dt.datetime.now(dt.timezone.utc)
    job.error = error
    db.commit()
    db.refresh(job)
