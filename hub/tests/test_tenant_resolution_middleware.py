"""
Phase 1: TenantResolutionMiddleware must resolve exactly one publisher_id
per request, or reject the request before any route handler runs.
"""
from __future__ import annotations

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from app.core.security import generate_installation_token, hash_token
from app.core.tenancy import TenantResolutionMiddleware, get_current_tenant
from app.db.models.publisher import Publisher, PublisherInstallation


def _build_test_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(TenantResolutionMiddleware)

    @app.get("/whoami")
    def whoami(tenant=Depends(get_current_tenant)):
        return {"publisher_id": tenant.publisher_id, "installation_id": tenant.installation_id}

    return app


def _seed_installation(db_session, slug: str = "buddy-magazine"):
    publisher = Publisher(slug=slug, name=slug)
    db_session.add(publisher)
    db_session.flush()

    token = generate_installation_token()
    installation = PublisherInstallation(
        publisher_id=publisher.id,
        site_id="test-site",
        site_url="https://example.test",
        credential_hash=hash_token(token),
        status="active",
    )
    db_session.add(installation)
    db_session.commit()
    return publisher, installation, token


def test_missing_credential_is_rejected_before_the_route_runs(db_session):
    client = TestClient(_build_test_app())

    response = client.get("/whoami")

    assert response.status_code == 401


def test_unknown_credential_is_rejected(db_session):
    client = TestClient(_build_test_app())

    response = client.get("/whoami", headers={"Authorization": "Bearer sfhub_not-a-real-token"})

    assert response.status_code == 401


def test_valid_credential_resolves_to_its_own_publisher_only(db_session):
    publisher, installation, token = _seed_installation(db_session)
    client = TestClient(_build_test_app())

    response = client.get("/whoami", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    body = response.json()
    assert body["publisher_id"] == publisher.id
    assert body["installation_id"] == installation.id


def test_inactive_installation_is_treated_as_no_credential(db_session):
    publisher, installation, token = _seed_installation(db_session)
    installation.status = "revoked"
    db_session.commit()
    client = TestClient(_build_test_app())

    response = client.get("/whoami", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401


def test_public_paths_bypass_tenant_resolution_entirely():
    client = TestClient(_build_test_app())

    response = client.get("/health")

    # Not registered on this test app, but the middleware must not 401 it
    # into a tenant-resolution failure -- it should fall through to a
    # normal 404 from routing, proving PUBLIC_PATHS skip resolution.
    assert response.status_code == 404
