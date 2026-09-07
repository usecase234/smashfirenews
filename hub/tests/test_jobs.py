"""
Phase 4: job queue status transitions and idempotency
(docs/Smashfire_PR_Starting_Build_Plan.md).

Exercises the generate-draft enqueue endpoint, the job status endpoint, and
app/services/jobs.py's transitions directly. `fake_arq_redis` (an autouse
fixture in tests/conftest.py) stands in for a real Redis connection, so
these tests never require a live worker or broker.
"""
from __future__ import annotations

from fastapi.testclient import TestClient

from app.core.security import generate_installation_token, hash_token
from app.db.models.publisher import Publisher, PublisherInstallation
from app.main import app
from app.services import jobs as jobs_service
from app.workers.worker import run_action

client = TestClient(app)


def _seed_installation(db_session, slug: str):
    publisher = Publisher(slug=slug, name=slug)
    db_session.add(publisher)
    db_session.flush()

    token = generate_installation_token()
    installation = PublisherInstallation(
        publisher_id=publisher.id,
        site_id=f"{slug}-site",
        site_url=f"https://{slug}.example",
        credential_hash=hash_token(token),
        status="active",
    )
    db_session.add(installation)
    db_session.commit()
    return publisher, token


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _submit(token: str) -> dict:
    response = client.post(
        "/submissions",
        json={
            "headline": "Buddy signs new headliner",
            "body_text": "Original release text.",
            "sender_name": "Pat Publicist",
            "sender_email": "pat@example.com",
        },
        headers=_auth(token),
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_enqueueing_creates_a_queued_job_and_pushes_to_redis_once(db_session, fake_arq_redis):
    _, token = _seed_installation(db_session, "buddy-magazine")
    submission = _submit(token)

    response = client.post(f"/submissions/{submission['id']}/generate-draft", headers=_auth(token))

    assert response.status_code == 202, response.text
    body = response.json()
    assert body["status"] == "queued"
    assert body["action"] == "generate_publisher_draft"
    assert body["attempts"] == 0
    assert body["submission_id"] == submission["id"]
    assert body["started_at"] is None
    assert body["finished_at"] is None

    assert len(fake_arq_redis.enqueued) == 1
    function, args, kwargs = fake_arq_redis.enqueued[0]
    assert function == "run_action_job"
    assert args == (body["id"],)
    assert kwargs["_job_id"] == f"generate_publisher_draft:{submission['id']}"


def test_enqueueing_twice_while_active_returns_the_existing_job(db_session, fake_arq_redis):
    _, token = _seed_installation(db_session, "buddy-magazine")
    submission = _submit(token)

    first = client.post(f"/submissions/{submission['id']}/generate-draft", headers=_auth(token))
    second = client.post(f"/submissions/{submission['id']}/generate-draft", headers=_auth(token))

    assert first.status_code == 202
    assert second.status_code == 202
    assert first.json()["id"] == second.json()["id"]
    # The second call found the still-queued job and never enqueued a
    # duplicate onto the (fake) queue.
    assert len(fake_arq_redis.enqueued) == 1


def test_enqueueing_again_after_the_job_finishes_creates_a_new_job(db_session):
    publisher, token = _seed_installation(db_session, "buddy-magazine")
    submission = _submit(token)

    first = client.post(f"/submissions/{submission['id']}/generate-draft", headers=_auth(token)).json()
    job = jobs_service.get_job(db_session, publisher.id, first["id"])
    run_action(db_session, job)
    assert job.status == "succeeded"

    second = client.post(f"/submissions/{submission['id']}/generate-draft", headers=_auth(token)).json()

    assert second["id"] != first["id"]


def test_status_transitions_queued_to_running_to_succeeded(db_session):
    publisher, token = _seed_installation(db_session, "buddy-magazine")
    submission = _submit(token)

    created = client.post(f"/submissions/{submission['id']}/generate-draft", headers=_auth(token)).json()
    job = jobs_service.get_job(db_session, publisher.id, created["id"])
    assert job.status == "queued"
    assert job.attempts == 0
    assert job.started_at is None
    assert job.finished_at is None

    run_action(db_session, job)

    assert job.status == "succeeded"
    assert job.attempts == 1
    assert job.started_at is not None
    assert job.finished_at is not None
    assert job.error is None


def test_a_failing_run_is_retryable_until_max_attempts_then_goes_dead(db_session):
    publisher, token = _seed_installation(db_session, "buddy-magazine")
    submission = _submit(token)

    created = client.post(f"/submissions/{submission['id']}/generate-draft", headers=_auth(token)).json()
    job = jobs_service.get_job(db_session, publisher.id, created["id"])

    # Drives app/services/jobs.py's transitions directly -- the stub
    # handler can't fail on its own, and failure/retry orchestration is
    # arq's job in production, not something this phase re-implements.
    jobs_service.mark_running(db_session, job)
    jobs_service.mark_failed(db_session, job, "boom")
    assert (job.status, job.attempts) == ("failed", 1)

    jobs_service.mark_running(db_session, job)
    jobs_service.mark_failed(db_session, job, "boom again")
    assert (job.status, job.attempts) == ("failed", 2)

    jobs_service.mark_running(db_session, job)
    jobs_service.mark_failed(db_session, job, "boom a third time")
    assert (job.status, job.attempts) == ("dead", jobs_service.MAX_ATTEMPTS)


def test_job_status_endpoint_returns_current_state(db_session):
    _, token = _seed_installation(db_session, "buddy-magazine")
    submission = _submit(token)
    created = client.post(f"/submissions/{submission['id']}/generate-draft", headers=_auth(token)).json()

    response = client.get(f"/jobs/{created['id']}", headers=_auth(token))

    assert response.status_code == 200
    assert response.json() == created


def test_job_status_endpoint_is_tenant_scoped(db_session):
    _, buddy_token = _seed_installation(db_session, "buddy-magazine")
    _, other_token = _seed_installation(db_session, "some-other-publisher")
    submission = _submit(buddy_token)
    created = client.post(
        f"/submissions/{submission['id']}/generate-draft", headers=_auth(buddy_token)
    ).json()

    other = client.get(f"/jobs/{created['id']}", headers=_auth(other_token))

    assert other.status_code == 404


def test_job_status_endpoint_404s_for_unknown_id(db_session):
    _, token = _seed_installation(db_session, "buddy-magazine")

    response = client.get("/jobs/999999", headers=_auth(token))

    assert response.status_code == 404
