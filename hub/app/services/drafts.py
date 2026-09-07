"""
The `generate_publisher_draft` constrained action.

Phase 3 stub: echoes the submission's immutable original text back as the
draft body, tagged `stub-v1`, so the queue -> draft -> publish pipes are
proven before Phase 4 wires this into a real model call. Per the hard rule
against overwriting editorial output in place, this always inserts a new
DraftVersion row rather than mutating an existing one — even the stub
respects the versioning contract Phase 4's rewrite_draft action depends on.
"""
from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models.submission import DraftVersion, Submission

STUB_GENERATOR_TAG = "stub-v1"


def generate_publisher_draft(db: Session, submission: Submission) -> DraftVersion:
    next_version = (
        db.execute(
            select(func.coalesce(func.max(DraftVersion.version), 0)).where(
                DraftVersion.submission_id == submission.id
            )
        ).scalar_one()
        + 1
    )
    draft = DraftVersion(
        publisher_id=submission.publisher_id,
        submission_id=submission.id,
        version=next_version,
        body_text=submission.body_text,
        generator=STUB_GENERATOR_TAG,
    )
    db.add(draft)
    if submission.status == "queued":
        submission.status = "drafted"
    db.commit()
    db.refresh(draft)
    return draft
