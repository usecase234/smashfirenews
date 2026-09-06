"""
Tenant-resolution middleware.

Every authenticated request must resolve to exactly one publisher_id before
any route handler runs — routes never accept a publisher/tenant id from the
client (query param, header, body) and use it directly. The middleware is
the single place a bearer credential is turned into a trusted `TenantContext`.

See docs/Smashfire_PR_Starting_Build_Plan.md, Phase 1, and the "Hub credential
separation" table in docs/Smashfire_PR_Full_Product_Technical_Plan_2026.md
(WP installation secret row).
"""
from __future__ import annotations

from dataclasses import dataclass

from fastapi import Request
from sqlalchemy.orm import Session, sessionmaker
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import JSONResponse
from starlette.types import ASGIApp

from app.core.security import hash_token
from app.db.models.publisher import PublisherInstallation
from app.db.session import SessionLocal

# Paths that intentionally have no tenant — infra/meta endpoints only.
# Nothing product-specific belongs on this list.
PUBLIC_PATHS = {"/health", "/docs", "/redoc", "/openapi.json"}


@dataclass(frozen=True)
class TenantContext:
    """The trusted result of resolving a request's credential."""

    publisher_id: int
    installation_id: int


def resolve_tenant_from_token(db: Session, token: str | None) -> TenantContext | None:
    """Look up the installation for a bearer token and return its tenant.

    Returns None for a missing/unknown/inactive credential — callers must
    treat that as "no tenant," never fall back to a default publisher_id.
    """
    if not token:
        return None
    installation = (
        db.query(PublisherInstallation)
        .filter(
            PublisherInstallation.credential_hash == hash_token(token),
            PublisherInstallation.status == "active",
        )
        .one_or_none()
    )
    if installation is None:
        return None
    return TenantContext(publisher_id=installation.publisher_id, installation_id=installation.id)


def _extract_bearer_token(request: Request) -> str | None:
    header = request.headers.get("authorization", "")
    scheme, _, token = header.partition(" ")
    if scheme.lower() != "bearer" or not token:
        return None
    return token


class TenantResolutionMiddleware(BaseHTTPMiddleware):
    """Resolves `request.state.tenant` from the Authorization header.

    Requests to PUBLIC_PATHS pass through with no tenant. Every other
    request either gets a resolved `TenantContext` on `request.state.tenant`
    or a 401 before any route code runs.
    """

    def __init__(self, app: ASGIApp, session_factory: sessionmaker = SessionLocal) -> None:
        super().__init__(app)
        self._session_factory = session_factory

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        if request.url.path in PUBLIC_PATHS:
            return await call_next(request)

        token = _extract_bearer_token(request)
        db = self._session_factory()
        try:
            tenant = resolve_tenant_from_token(db, token)
        finally:
            db.close()

        if tenant is None:
            return JSONResponse(
                status_code=401,
                content={"detail": "missing or invalid installation credential"},
            )

        request.state.tenant = tenant
        return await call_next(request)


def get_current_tenant(request: Request) -> TenantContext:
    """FastAPI dependency: the tenant resolved by TenantResolutionMiddleware.

    Route handlers depend on this instead of ever reading a publisher_id
    off the request directly.
    """
    tenant = getattr(request.state, "tenant", None)
    if tenant is None:
        # Only reachable if a route forgets to sit behind the middleware,
        # or is misconfigured as a public path while still being tenant-scoped.
        raise RuntimeError(
            "no TenantContext on request.state — route is not behind "
            "TenantResolutionMiddleware or was wrongly added to PUBLIC_PATHS"
        )
    return tenant
