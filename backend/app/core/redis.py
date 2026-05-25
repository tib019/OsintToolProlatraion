from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

import redis.asyncio as aioredis
from redis.asyncio import Redis

from app.core.config import settings


# Module-level Redis client (initialised lazily on first use)
_redis_client: Redis | None = None


def _get_client() -> Redis:
    """Return (or create) the module-level Redis client."""
    global _redis_client
    if _redis_client is None:
        _redis_client = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
    return _redis_client


async def get_redis() -> AsyncGenerator[Redis, None]:
    """
    FastAPI dependency that yields a Redis client.

    Usage::

        @router.get("/example")
        async def example(redis: Redis = Depends(get_redis)):
            value = await redis.get("key")
    """
    client = _get_client()
    try:
        yield client
    finally:
        # The shared client is not closed here; it lives for the application
        # lifetime.  Call close_redis() during application shutdown instead.
        pass


@asynccontextmanager
async def redis_context() -> AsyncGenerator[Redis, None]:
    """
    Async context manager for one-off Redis access outside of a request
    lifecycle (e.g. background tasks, scripts).

    Usage::

        async with redis_context() as redis:
            await redis.set("key", "value")
    """
    client = _get_client()
    try:
        yield client
    finally:
        pass


async def close_redis() -> None:
    """Close the shared Redis connection pool.  Call during app shutdown."""
    global _redis_client
    if _redis_client is not None:
        await _redis_client.aclose()
        _redis_client = None
