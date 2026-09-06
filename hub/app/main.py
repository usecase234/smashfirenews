"""
Smashfire PR Hub — application entrypoint.

Phase 0: nothing but a health check. Tenancy, submissions, AI routing etc.
are added in later phases per docs/Smashfire_PR_Starting_Build_Plan.md.
"""
from fastapi import FastAPI

from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title="Smashfire PR Hub",
    version="0.0.1",
    description="Multi-tenant control plane for Smashfire PR. "
    "Owns tenant identity, submissions, AI routing, assets, quotas and billing.",
)


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": "smashfire-pr-hub",
        "env": settings.environment,
    }
