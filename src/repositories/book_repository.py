from db import DataBase
from db.models import Author, Book


class BookRepository:
    def __init__(self, db: DataBase):
        self.db = db

    async def get_most_recent_books(self, limit: int = 20) -> list[Book]:
        records = await self.db.run_query("get_most_recent_books", limit=limit)
        return Book.from_db_records(records)

    async def insert_book(self, book: Book):
        print("checking if book exists")
        existing_book = await self.db.run_query("get_book_by_openlib_work_key", openlib_work_key=book.openlib_work_key)

        if existing_book:
            print("book already exists")
            return
        return await self.db.run_query("insert_book", **book.to_db_dict())

    async def insert_author(self, author: Author):
        print("checking if author exists")
        existing_author = await self.db.run_query("get_author_by_openlib_id", openlib_id=author.openlib_id)

        if existing_author:
            print("author already exists")
            return
        return await self.db.run_query("insert_author", **author.to_db_dict())
