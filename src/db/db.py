import aiosql
import asyncpg
from pathlib import Path
from typing import Any, Optional

from db.models import Author, Book


class DataBase:
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

    async def set_queries(self):
        if self.queries is None:
            dir_path = Path(__file__).parent
            self.queries = aiosql.from_path(dir_path / "sql", driver_adapter="asyncpg")
        return self.queries

    async def close_down(self):
        if self.pool:
            await self.pool.close()

    async def create_schema(self):
        self.queries = self.set_queries()

        async with self.pool.acquire() as conn:
            print("setting up db schema")
            self.queries = await self.queries.create_schema(conn)

    async def insert_author(self, author: Author):
        self.queries = self.set_queries()

        async with self.pool.acquire() as conn:
            print("checking if author exists")
            existing_author = await self.queries.get_author_by_openlib_id(conn, openlib_id=author.openlib_id)

            if existing_author:
                print("author already exists")
                return
            return await self.queries.insert_author(conn, **author.to_db_dict())

    async def insert_book(self, book: Book):
        self.queries = self.set_queries()

        async with self.pool.acquire() as conn:
            print("checking if book exists")
            existing_book = await self.queries.get_book_by_openlib_work_key(
                conn, openlib_work_key=book.openlib_work_key
            )

            if existing_book:
                print("book already exists")
                return
            return await self.queries.insert_book(conn, **book.to_db_dict())
