from asyncpg import Record

from db import DataBase
from db.models import Author, Book
from repositories.utils import one_or_none


class BookRepository:
    def __init__(self, db: DataBase):
        self.db = db

    """ Insert values """

    async def insert_book(self, book: Book) -> int:
        """
        Returns id of created book
        """
        return await self.db.run_query("insert_book", **book.to_db_dict())

    async def insert_author(self, author: Author):
        return await self.db.run_query("insert_author", **author.to_db_dict())

    async def insert_review(self, user_id: int, book_id: int, content: str):
        return await self.db.run_query("insert_review", user_id=user_id, book_id=book_id, content=content)

    """ Get or read values """

    async def get_most_recent_books(self, limit: int = 20) -> list[Book]:
        records = await self.db.run_query("get_most_recent_books", limit=limit)
        return Book.from_db_records(records)

    async def get_book_by_openlib_id(self, openlib_work_key: str = "") -> Record | None:
        return one_or_none(await self.db.run_query("get_book_by_openlib_work_key", openlib_work_key=openlib_work_key))

    async def get_book_id_by_openlib_id(self, openlib_work_key: str = "") -> Record | None:
        return one_or_none(
            await self.db.run_query("get_book_id_by_openlib_work_key", openlib_work_key=openlib_work_key)
        )

    async def get_user_id_by_username(self, username: str):
        return one_or_none(await self.db.run_query("get_user_id_by_username", username=username))

    """ Check values """

    async def check_if_author_exists(self, author_openlib_id: str) -> bool:
        print("checking if author exists")
        return bool(await self.db.run_query("get_author_by_openlib_id", openlib_id=author_openlib_id))
