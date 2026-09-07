"""
Test DB setup.

Points DATABASE_URL at a scratch SQLite file *before* any `app` module is
imported, so `app.db.session.engine` is built against it rather than the
Postgres URL used in dev/prod. Every test gets a clean schema.
"""
import os
import tempfile
from pathlib import Path

_TEST_DB_PATH = Path(tempfile.gettempdir()) / "smashfire_hub_test.db"
os.environ["DATABASE_URL"] = f"sqlite+pysqlite:///{_TEST_DB_PATH}"

import pytest  # noqa: E402

from app.core.queue import get_arq_redis  # noqa: E402
from app.db.base import Base  # noqa: E402
from app.db.session import SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(autouse=True)
def _clean_schema():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture
def db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


class FakeArqRedis:
    """Records enqueue_job calls instead of talking to a real Redis.

    Nothing in the test suite runs a live arq worker process; tests that
    need a job to actually execute call app.workers.worker.run_action
    directly (see tests/test_jobs.py) rather than going through Redis.
    """

    def __init__(self):
        self.enqueued: list[tuple] = []

    async def enqueue_job(self, function, *args, **kwargs):
        self.enqueued.append((function, args, kwargs))


@pytest.fixture(autouse=True)
def fake_arq_redis():
    fake = FakeArqRedis()
    app.dependency_overrides[get_arq_redis] = lambda: fake
    yield fake
    app.dependency_overrides.pop(get_arq_redis, None)
