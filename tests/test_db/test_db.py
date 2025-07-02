import asyncpg
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from db import Database


@pytest.fixture
def db():
    with patch("asyncpg.create_pool", new_callable=AsyncMock) as mock_create_pool:
        db_instance = Database(user="test_user", password="test_password", url="test_url")
        db_instance.pool = mock_create_pool.return_value
        yield db_instance


@pytest.mark.asyncio
async def test_database_init(db: Database):
    assert db.dsn == "postgresql://test_user:test_password@test_url"
    assert db.pool is not None
    assert db.queries is None


@pytest.mark.asyncio
async def test_startup(db: Database):
    with (
        patch.object(db, "set_queries", new_callable=AsyncMock) as mock_set_queries,
        patch.object(db, "create_schema", new_callable=AsyncMock) as mock_create_schema,
    ):
        await db.start_up()

        asyncpg.create_pool.assert_called_once()
        mock_set_queries.assert_awaited_once()
        mock_create_schema.assert_awaited_once()


@pytest.mark.asyncio
async def test_close_down(db: Database):
    db.pool.close = AsyncMock()
    await db.close_down()
    db.pool.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_run_query(db: Database):
    db.queries = MagicMock()
    db.queries.test_query = AsyncMock(return_value="test_result")
    db.pool.acquire = MagicMock()

    mock_conn = AsyncMock()
    db.pool.acquire.return_value.__aenter__.return_value = mock_conn

    result = await db.run_query("test_query", param="value")

    assert result == "test_result"
    db.queries.test_query.assert_awaited_once_with(mock_conn, param="value")


@pytest.mark.asyncio
async def test_create_schema(db: Database):
    with patch.object(db, "run_query", new_callable=AsyncMock) as mock_run_query:
        await db.create_schema()
        mock_run_query.assert_awaited_once_with("create_schema")


@pytest.mark.asyncio
async def test_async_context_manager():
    with (
        patch("db.Database.start_up", new_callable=AsyncMock) as mock_start_up,
        patch("db.Database.close_down", new_callable=AsyncMock) as mock_close_down,
    ):
        async with Database(user="test", password="test", url="test") as db:
            assert db
            mock_start_up.assert_awaited_once()
            assert not mock_close_down.called

        mock_close_down.assert_awaited_once()
