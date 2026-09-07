"""
arq worker entrypoint for Phase 4's async AI actions
(docs/Smashfire_PR_Starting_Build_Plan.md).

Runs as a separate Railway service from the API process, consuming the
same Redis instance the Hub already depends on
(`redis://` inside the `industrious-intuition` project's private network).
Imports app/core/config.py rather than reading REDIS_URL/DATABASE_URL
independently, so the `postgresql+psycopg://` DATABASE_URL normalization
(CLAUDE.md hard rule) and every other Settings default apply to the worker
exactly as they do to the API process.

Start with: `arq app.workers.worker.WorkerSettings`

Phase 4 scope note: only `generate_publisher_draft` has a real handler
right now -- the Phase 3 echo stub, unchanged. The other four constrained
actions (`analyze_submission`, `rewrite_draft`, `generate_headlines`,
`classify_relevance`) get their own handlers once the prompt service/AI
router land. ACTION_HANDLERS *is* the enforcement of "no generic
prompt-passthrough endpoint" at the worker layer: a job's `action` string
can only ever dispatch to one of these named functions.
"""
from __future__ import annotations

from typing import ClassVar

from arq.connections import RedisSettings
from arq.worker import func
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.models.jobs import Job
from app.db.session import SessionLocal
from app.services import jobs as jobs_service
from app.services.drafts import generate_publisher_draft
from app.services.submissions import get_submission

ACTION_HANDLERS = {
    "generate_publisher_draft": generate_publisher_draft,
}


def run_action(db: Session, job: Job) -> None:
    """Executes one job's constrained action and records the outcome.

    Synchronous and DB-only -- kept separate from the arq task function so
    it can be exercised directly in tests without a Redis connection or an
    event loop (see hub/tests/test_jobs.py).
    """
    jobs_service.mark_running(db, job)
    try:
        submission = get_submission(db, job.publisher_id, job.submission_id)
        if submission is None:
            raise LookupError(f"submission {job.submission_id} not found for job {job.id}")
        handler = ACTION_HANDLERS[job.action]
        handler(db, submission)
    except Exception as exc:
        jobs_service.mark_failed(db, job, str(exc))
        raise
    else:
        jobs_service.mark_succeeded(db, job)


async def run_action_job(ctx, job_id: int) -> None:
    """The one arq task function every job in the queue runs through."""
    db = SessionLocal()
    try:
        job = db.get(Job, job_id)
        if job is None:
            return
        run_action(db, job)
    finally:
        db.close()


class WorkerSettings:
    """arq worker entrypoint: `arq app.workers.worker.WorkerSettings`.

    `max_tries` mirrors app/services/jobs.py's MAX_ATTEMPTS so arq's own
    retry ceiling and this module's failed-vs-dead bookkeeping never
    disagree about when a job is done retrying.
    """

    functions: ClassVar = [func(run_action_job, max_tries=jobs_service.MAX_ATTEMPTS)]
    redis_settings = RedisSettings.from_dsn(get_settings().redis_url)
