"""
Smashfire PR Hub — application entrypoint.

Phase 1 adds the tenancy skeleton: every non-public request is resolved to
a publisher_id by TenantResolutionMiddleware before any route runs.
Submissions, AI routing, etc. are added in later phases per
docs/Smashfire_PR_Starting_Build_Plan.md.
"""
from fastapi import FastAPI

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


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": "smashfire-pr-hub",
        "env": settings.environment,
    }
