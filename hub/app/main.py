"""
Smashfire PR Hub — application entrypoint.

Phase 1 adds the tenancy skeleton: every non-public request is resolved to
a publisher_id by TenantResolutionMiddleware before any route runs. Phase 3
adds the submissions vertical slice (intake, queues, the stubbed
generate_publisher_draft action, publish-provenance recording). Phase 4
adds the job queue (app/api/jobs.py, app/services/jobs.py,
app/workers/worker.py): generate-draft now enqueues instead of running the
stub inline. See docs/Smashfire_PR_Starting_Build_Plan.md.
"""
from fastapi import FastAPI

from app.api.jobs import router as jobs_router
from app.api.submissions import router as submissions_router
from app.core.config import get_settings
from app.core.tenancy import TenantResolutionMiddleware

settings = get_settings()

app = FastAPI(
    title="Smashfire PR Hub",
    version="0.0.1",
    description="Multi-tenant control plane for Smashfire PR. "
    "Owns tenant identity, submissions, AI routing, assets, quotas and billing.",
)

app.add_middleware(TenantResolutionMiddleware)
app.include_router(submissions_router)
app.include_router(jobs_router)


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": "smashfire-pr-hub",
        "env": settings.environment,
    }
