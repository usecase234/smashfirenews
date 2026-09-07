"""
Phase 3: the thin vertical slice (docs/Smashfire_PR_Starting_Build_Plan.md).

Covers the happy path end to end (submit -> queue -> generate-draft ->
finished drafts -> publish) plus the two architectural rules this phase is
required to encode a test for: tenant isolation on the new tables, and
"original submissions are immutable; drafts are versioned, never
overwritten in place" (CLAUDE.md hard rules).

Phase 4 changed generate-draft from a synchronous call into an enqueue
(see tests/test_jobs.py for the job-queue-specific tests). There's no live
arq worker process in tests, so these tests simulate one by calling
app.workers.worker.run_action directly against the job the enqueue call
created -- the same function the real worker's arq task wraps.
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


def _submit(token: str, headline: str = "Buddy signs new headliner") -> dict:
    response = client.post(
        "/submissions",
        json={
            "headline": headline,
            "body_text": "Original release text, verbatim from the publicist.",
            "sender_name": "Pat Publicist",
            "sender_email": "pat@example.com",
            "sender_company": "Example PR",
        },
        headers=_auth(token),
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_submission_to_publish_end_to_end(db_session):
    publisher, token = _seed_installation(db_session, "buddy-magazine")

    submission = _submit(token)
    submission_id = submission["id"]
    assert submission["status"] == "queued"

    queue = client.get("/submissions", params={"status": "queued"}, headers=_auth(token)).json()
    assert [s["id"] for s in queue] == [submission_id]

    enqueued = client.post(f"/submissions/{submission_id}/generate-draft", headers=_auth(token))
    assert enqueued.status_code == 202, enqueued.text
    job_body = enqueued.json()
    assert job_body["status"] == "queued"
    assert job_body["action"] == "generate_publisher_draft"

    # No live arq worker in tests -- run the job's handler directly, the
    # same function the worker's arq task calls.
    job = jobs_service.get_job(db_session, publisher.id, job_body["id"])
    run_action(db_session, job)
    assert job.status == "succeeded"

    detail = client.get(f"/submissions/{submission_id}", headers=_auth(token)).json()
    assert len(detail["drafts"]) == 1
    draft_body = detail["drafts"][0]
    assert draft_body["version"] == 1
    assert draft_body["generator"] == "stub-v1"
    assert draft_body["body_text"] == submission["body_text"]

    finished = client.get("/submissions", params={"status": "drafted"}, headers=_auth(token)).json()
    assert [s["id"] for s in finished] == [submission_id]

    publish = client.post(
        f"/submissions/{submission_id}/publish",
        json={"wp_post_id": 42, "live_url": "https://buddymagazine.example/2026/09/headliner"},
        headers=_auth(token),
    )
    assert publish.status_code == 200, publish.text
    published = publish.json()
    assert published["status"] == "published"
    assert published["wp_post_id"] == 42
    assert published["live_url"] == "https://buddymagazine.example/2026/09/headliner"
    assert published["published_at"] is not None


def test_cannot_publish_without_a_generated_draft(db_session):
    _, token = _seed_installation(db_session, "buddy-magazine")
    submission = _submit(token)

    response = client.post(
        f"/submissions/{submission['id']}/publish",
        json={"wp_post_id": 1, "live_url": "https://buddymagazine.example/x"},
        headers=_auth(token),
    )

    assert response.status_code == 409


def test_generating_a_draft_never_touches_the_original_and_never_overwrites_a_prior_version(db_session):
    publisher, token = _seed_installation(db_session, "buddy-magazine")
    submission = _submit(token)
    submission_id = submission["id"]

    def _generate_and_run():
        response = client.post(f"/submissions/{submission_id}/generate-draft", headers=_auth(token))
        assert response.status_code == 202, response.text
        job = jobs_service.get_job(db_session, publisher.id, response.json()["id"])
        run_action(db_session, job)
        assert job.status == "succeeded"
        return job

    # Each call only creates a new job because the previous one already
    # reached a terminal status by the time the next call is made -- while
    # a job is still queued/running, a second call must return it unchanged
    # (see tests/test_jobs.py for that behavior in isolation).
    first_job = _generate_and_run()
    second_job = _generate_and_run()

    assert first_job.id != second_job.id  # a new job, not the same one reused

    detail = client.get(f"/submissions/{submission_id}", headers=_auth(token)).json()
    assert detail["body_text"] == submission["body_text"]  # original untouched
    assert [d["version"] for d in detail["drafts"]] == [1, 2]


def test_a_tenants_submissions_are_invisible_to_another_tenant(db_session):
    _, buddy_token = _seed_installation(db_session, "buddy-magazine")
    _, other_token = _seed_installation(db_session, "some-other-publisher")

    buddy_submission = _submit(buddy_token, headline="Buddy-only release")

    # Not in the other tenant's queue at all.
    other_queue = client.get("/submissions", headers=_auth(other_token)).json()
    assert buddy_submission["id"] not in [s["id"] for s in other_queue]

    # Direct id lookup by the other tenant is a 404, not a 403 — existence
    # of another tenant's row must not leak either.
    direct = client.get(f"/submissions/{buddy_submission['id']}", headers=_auth(other_token))
    assert direct.status_code == 404

    # Nor can the other tenant drive its lifecycle actions.
    generate = client.post(
        f"/submissions/{buddy_submission['id']}/generate-draft", headers=_auth(other_token)
    )
    assert generate.status_code == 404
