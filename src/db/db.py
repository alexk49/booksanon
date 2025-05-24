from pathlib import Path
import aiosql
import asyncpg


class DataBase:
    def __init__(self, user: str, password: str, url: str):
        self.dsn = f"postgresql://{user}:{password}@{url}"
        self.pool: asyncpg.Pool = None
        self.queries = None

    async def __aenter__(self):
        await self.start_up()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.close_down()

    async def start_up(self):
        self.pool = await asyncpg.create_pool(dsn=self.dsn)
        self.queries = await self.set_queries()

    async def set_queries(self):
        if self.queries is None:
            dir_path = Path(__file__).parent
            self.queries = aiosql.from_path(dir_path / "sql", driver_adapter="asyncpg")
        return self.queries

    async def close_down(self):
        if self.pool:
            await self.pool.close()

    async def create_schema(self):
        async with self.pool.acquire() as conn:
            print("setting up db schema")
            await self.queries.create_schema(conn)
