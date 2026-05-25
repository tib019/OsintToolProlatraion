"""
Pytest configuration and shared fixtures for the PHANTOM backend test suite.
"""
from __future__ import annotations

from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.db.base import Base  # import all models so metadata is populated
from app.db.session import get_db
from app.main import app

# ---------------------------------------------------------------------------
# In-memory SQLite engine (per test session)
# ---------------------------------------------------------------------------

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)

_TestingSessionLocal = async_sessionmaker(
    bind=_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# ---------------------------------------------------------------------------
# Schema setup / teardown
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database() -> AsyncGenerator[None, None]:
    """Create all tables once per test session; drop them afterwards."""
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await _engine.dispose()


# ---------------------------------------------------------------------------
# Per-test DB session (rolled back after each test)
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture()
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Yield an async SQLAlchemy session backed by an in-memory SQLite database.

    Each test runs inside a transaction that is rolled back on teardown so
    tests remain isolated without truncating tables.
    """
    async with _engine.connect() as conn:
        await conn.begin()

        session = AsyncSession(bind=conn, expire_on_commit=False)
        try:
            yield session
        finally:
            await session.close()
            await conn.rollback()


# ---------------------------------------------------------------------------
# FastAPI test client with DB override
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture()
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Yield an ``httpx.AsyncClient`` wired to the FastAPI app.

    The ``get_db`` dependency is overridden to use the test's in-memory
    SQLite session so HTTP requests hit the same transactional context.
    """

    async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
