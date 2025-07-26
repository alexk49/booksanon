import aiosql
import asyncpg
import logging
from pathlib import Path
from typing import Any, Optional


logger = logging.getLogger(__name__)


class Database:
    def __init__(self, user: str, password: str, url: str):
        self.dsn = f"postgresql://{user}:{password}@{url}"
        self.pool: asyncpg.Pool = None
        self.queries: Optional[Any] = None

    async def __aenter__(self):
        await self.start_up()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.close_down()

    async def start_up(self):
        self.pool = await asyncpg.create_pool(dsn=self.dsn)
        self.queries = await self.set_queries()
        await self.create_schema()

    async def set_queries(self):
        if self.queries is None:
            dir_path = Path(__file__).parent
            self.queries = aiosql.from_path(dir_path / "sql", driver_adapter="asyncpg")
        return self.queries

    async def close_down(self):
        if self.pool:
            await self.pool.close()

    async def run_query(self, query_name, **kwargs):
        """
        Can be used for most straight forward queries,
        will have to have matching sql file set.

        Expectation is to be called from repositories modules
        """
        self.queries = await self.set_queries()

        async with self.pool.acquire() as conn:
            query_method = getattr(self.queries, query_name)
            return await query_method(conn, **kwargs)

    async def create_schema(self):
        logger.info("setting up db schema")
        await self.run_query("create_schema")
