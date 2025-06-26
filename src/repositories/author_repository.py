from asyncpg import Record

from db import Database
from db.models import Author


class AuthorRepository:
    def __init__(self, db: Database):
        self.db = db

    """ Insert values """

    async def insert_author(self, author: Author):
        return await self.db.run_query("insert_author", **author.to_db_dict())

    """ Get or read values """

    async def get_author_by_id(self, author_id: int) -> Author:
        record = await self.db.run_query("get_author_by_id", author_id=author_id)
        if not record:
            return None
        return Author.from_db_record(record)

    async def get_author_id_by_openlib_id(self, author_openlib_id: str) -> Record | None:
        result = await self.db.run_query("get_author_id_by_openlib_id", openlib_id=author_openlib_id)
        return result["id"]

    """ Check values """

    async def check_if_author_exists(self, author_openlib_id: str) -> bool:
        print("checking if author exists")
        return bool(await self.db.run_query("get_author_by_openlib_id", openlib_id=author_openlib_id))
