"""
Lazy singleton arq Redis pool used by API routes to enqueue jobs.

Kept separate from app/workers/worker.py (the consumer side) so a route
can enqueue a job without importing worker/task code. `get_arq_redis` is a
FastAPI dependency specifically so tests can override it with a fake
instead of needing a real Redis connection -- see hub/tests/conftest.py.
"""
from __future__ import annotations

from arq import ArqRedis
from arq.connections import RedisSettings, create_pool

from app.core.config import get_settings

_pool: ArqRedis | None = None


async def get_arq_redis() -> ArqRedis:
    global _pool
    if _pool is None:
        _pool = await create_pool(RedisSettings.from_dsn(get_settings().redis_url))
    return _pool
