"""
Job status endpoint: the plugin polls this instead of the Hub returning a
generated draft synchronously. See app/services/jobs.py for the
queued/running/succeeded/failed/dead lifecycle these rows track.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.schemas import JobOut
from app.core.tenancy import TenantContext, get_current_tenant
from app.db.session import get_db
from app.services import jobs as jobs_service

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/{job_id}", response_model=JobOut)
def get_job(
    job_id: int,
    tenant: TenantContext = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    job = jobs_service.get_job(db, tenant.publisher_id, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="job not found")
    return job
