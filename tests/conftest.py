"""Shared test fixtures for insurance solution tests."""

from __future__ import annotations

import aios.agents.store.tables  # noqa: F401
import aios.auth.store.tables  # noqa: F401
import aios.hub.store.tables  # noqa: F401

# Import ALL table modules so they register with Base.metadata
import aios.ontology.store.tables  # noqa: F401
import aios.versioning.store.tables  # noqa: F401
import pytest
from aios.store.tables.workflow_tables import Base
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine


@pytest.fixture
async def session_factory():
    """Create an in-memory SQLite session factory with all AIOS tables."""
    engine = create_async_engine("sqlite+aiosqlite://", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    sf = async_sessionmaker(engine, expire_on_commit=False)
    yield sf
    await engine.dispose()
