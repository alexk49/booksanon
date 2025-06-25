from asyncpg import Record

from db import DataBase
from db.models import Author, Book, Review
from repositories.utils import one_or_none


class BookRepository:
    def __init__(self, db: DataBase):
        self.db = db

    """ Insert values """

    async def create_anon(self):
        await self.db.run_query("create_anon")

    async def insert_book(self, book: Book) -> int:
        """
        Returns id of created book
        """
        return await self.db.run_query("insert_book", **book.to_db_dict())

    async def insert_author(self, author: Author):
        return await self.db.run_query("insert_author", **author.to_db_dict())

    async def insert_review(self, user_id, book_id, review):
        return await self.db.run_query("insert_review", book_id=book_id, user_id=user_id, content=review)

    async def link_book_author(self, book_id: int, author_id: int):
        return await self.db.run_query("link_book_author", book_id=book_id, author_id=author_id)

    """ Get or read values """

    async def get_most_recent_books(self, limit: int = 10) -> list[Book]:
        records = await self.db.run_query("get_most_recent_books", limit=limit)
        return Book.from_db_records(records)

    async def get_book_by_openlib_id(self, openlib_work_key: str = "") -> Record | None:
        return one_or_none(await self.db.run_query("get_book_by_openlib_work_key", openlib_work_key=openlib_work_key))

    async def get_book_id_by_openlib_id(self, openlib_work_key: str) -> Record | None:
        return one_or_none(
            await self.db.run_query("get_book_id_by_openlib_work_key", openlib_work_key=openlib_work_key)
        )

    async def get_book_by_id(self, book_id: int) -> Record | None:
        result = one_or_none(await self.db.run_query("get_book_by_id", book_id=book_id))
        if result:
            return Book.from_db_record(result)
        return None

    async def get_author_by_id(self, author_id: int) -> Author:
        record = await self.db.run_query("get_author_by_id", author_id=author_id)
        if not record:
            return None
        return Author.from_db_record(record)

    async def get_books_by_author(self, author_id: int) -> list[Book]:
        records = await self.db.run_query("get_books_by_author", author_id=author_id)
        return Book.from_db_records(records)

    async def get_reviews_for_books(self, book_ids: list[int]) -> list[Review]:
        if not book_ids:
            return []
        records = await self.db.run_query("get_reviews_for_books", book_ids=book_ids)
        return [Review.from_db_record(r) for r in records] 

    async def get_author_id_by_openlib_id(self, author_openlib_id: str) -> Record | None:
        return one_or_none(await self.db.run_query("get_author_id_by_openlib_id", openlib_id=author_openlib_id))

    async def get_author_books_and_reviews(self, author_id: int) -> Record | None:
        records = await self.db.run_query("get_author_books_and_reviews", author_id=author_id)
        return records

    async def get_review_and_book_by_review_id(self, review_id: int):
        record = await self.db.run_query("get_review_and_book_by_review_id", review_id=review_id)
        return Review.from_db_record(record)

    """ search values """

    async def search_books(self, search_query: str):
        records = await self.db.run_query("search_books", search_query=search_query)
        return Book.from_db_records(records)

    """ Reviews """

    async def get_most_recent_book_reviews(self, limit: int = 10) -> list[Book]:
        records = await self.db.run_query("get_most_recent_book_reviews", limit=limit)
        return Review.from_db_records(records)

    async def get_book_and_reviews_by_book_id(self, book_id: int) -> tuple[Book, list[Review]]:
        records = await self.db.run_query("get_book_and_reviews_by_book_id", book_id=book_id)

        if not records:
            return None, []

        book = Book.from_db_record(records[0])

        reviews = []
        for r in records:
            # left join has possible null values
            if r:
                reviews.append(Review.from_joined_record(r))

        return book, reviews

    async def get_reviews_by_book_id(self, book_id: int) -> list[Book]:
        records = await self.db.run_query("get_reviews_by_book_id", book_id=book_id)
        return Review.from_db_records(records)

    async def get_user_id_by_username(self, username: str):
        return one_or_none(await self.db.run_query("get_user_id_by_username", username=username))

    """ Check values """

    async def check_if_author_exists(self, author_openlib_id: str) -> bool:
        print("checking if author exists")
        return bool(await self.db.run_query("get_author_by_openlib_id", openlib_id=author_openlib_id))
