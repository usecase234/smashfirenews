"""
Submission routes: intake, Pre-Writer/Finished-Drafts queues, the
`generate_publisher_draft` action, and publish-provenance recording.

Every route depends on `get_current_tenant`, which only exists once
TenantResolutionMiddleware has resolved a publisher_id — there is no route
here that accepts a tenant id from the caller.

Phase 4: generate-draft no longer runs the stub inline. It enqueues a job
(app/services/jobs.py) and returns 202 with the job's id/status; the arq
worker (app/workers/worker.py) is what actually calls
`generate_publisher_draft`. The plugin polls GET /jobs/{id}
(app/api/jobs.py) to learn when the draft is ready.
"""
from __future__ import annotations

from arq import ArqRedis
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.schemas import (
    JobOut,
    PublishRequest,
    SubmissionCreate,
    SubmissionDetail,
    SubmissionSummary,
)
from app.core.queue import get_arq_redis
from app.core.tenancy import TenantContext, get_current_tenant
from app.db.session import get_db
from app.services import jobs as jobs_service
from app.services import submissions as submission_service

GENERATE_PUBLISHER_DRAFT = "generate_publisher_draft"

router = APIRouter(prefix="/submissions", tags=["submissions"])


def _get_or_404(db: Session, publisher_id: int, submission_id: int):
    submission = submission_service.get_submission(db, publisher_id, submission_id)
    if submission is None:
        raise HTTPException(status_code=404, detail="submission not found")
    return submission


@router.post("", response_model=SubmissionDetail, status_code=201)
def create_submission(
    payload: SubmissionCreate,
    tenant: TenantContext = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    return submission_service.create_submission(db, tenant.publisher_id, payload)


@router.get("", response_model=list[SubmissionSummary])
def list_submissions(
    status: str | None = None,
    tenant: TenantContext = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    return submission_service.list_submissions(db, tenant.publisher_id, status)


@router.get("/{submission_id}", response_model=SubmissionDetail)
def get_submission(
    submission_id: int,
    tenant: TenantContext = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    return _get_or_404(db, tenant.publisher_id, submission_id)


@router.post("/{submission_id}/generate-draft", response_model=JobOut, status_code=202)
async def generate_draft(
    submission_id: int,
    tenant: TenantContext = Depends(get_current_tenant),
    db: Session = Depends(get_db),
    redis: ArqRedis = Depends(get_arq_redis),
):
    submission = _get_or_404(db, tenant.publisher_id, submission_id)
    job, created = jobs_service.get_or_create_job(
        db, tenant.publisher_id, submission.id, GENERATE_PUBLISHER_DRAFT
    )
    if created:
        await redis.enqueue_job("run_action_job", job.id, _job_id=job.idempotency_key)
    return job


@router.post("/{submission_id}/publish", response_model=SubmissionDetail)
def publish_submission(
    submission_id: int,
    payload: PublishRequest,
    tenant: TenantContext = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    submission = _get_or_404(db, tenant.publisher_id, submission_id)
    if not submission.drafts:
        raise HTTPException(status_code=409, detail="submission has no generated draft to publish")
    return submission_service.publish_submission(db, submission, payload.wp_post_id, payload.live_url)
