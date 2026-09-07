"""
Submission lifecycle: create (immutable original) -> queue -> publish.

Every read in this module goes through `tenant_scoped_select` — see
app/db/tenancy.py — so a submission can never be fetched, listed, or acted on
outside the tenant that owns it, even by id.
"""
from __future__ import annotations

import datetime as dt

from sqlalchemy.orm import Session, selectinload

from app.api.schemas import SubmissionCreate
from app.db.models.submission import Submission
from app.db.tenancy import tenant_scoped_select


def create_submission(db: Session, publisher_id: int, payload: SubmissionCreate) -> Submission:
    submission = Submission(publisher_id=publisher_id, status="queued", **payload.model_dump())
    db.add(submission)
    db.commit()
    db.refresh(submission)
    # Force-load now, while the request-scoped session is still open —
    # response serialization must not depend on session teardown timing.
    _ = submission.drafts
    return submission


def list_submissions(db: Session, publisher_id: int, status: str | None = None) -> list[Submission]:
    stmt = tenant_scoped_select(Submission, publisher_id).order_by(Submission.created_at.desc())
    if status is not None:
        stmt = stmt.where(Submission.status == status)
    return list(db.scalars(stmt).all())


def get_submission(db: Session, publisher_id: int, submission_id: int) -> Submission | None:
    # Eager-load drafts: response serialization must not depend on the
    # request-scoped session still being open by the time it runs.
    stmt = (
        tenant_scoped_select(Submission, publisher_id)
        .where(Submission.id == submission_id)
        .options(selectinload(Submission.drafts))
    )
    return db.scalars(stmt).one_or_none()


def publish_submission(db: Session, submission: Submission, wp_post_id: int, live_url: str) -> Submission:
    submission.status = "published"
    submission.wp_post_id = wp_post_id
    submission.live_url = live_url
    submission.published_at = dt.datetime.now(dt.timezone.utc)
    db.commit()
    db.refresh(submission)
    _ = submission.drafts
    return submission
