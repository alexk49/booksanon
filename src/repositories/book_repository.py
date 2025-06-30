from collections import defaultdict

from asyncpg import Record

from db import Database
from db.models import Book, Review
from .review_repository import ReviewRepository


class BookRepository:
    def __init__(self, db: Database, review_repo: ReviewRepository):
        self.db = db
        self.review_repo = review_repo

    """ Insert values """

    async def insert_book(self, book: Book) -> int:
        """
        Returns id of created book
        """
        return await self.db.run_query("insert_book", **book.to_db_dict())

    async def link_book_author(self, book_id: int, author_id: int) -> None:
        await self.db.run_query("link_book_author", book_id=book_id, author_id=author_id)

    """ Get or read values """

    async def get_most_recent_books(self, limit: int = 10) -> list[Book]:
        records = await self.db.run_query("get_most_recent_books", limit=limit)
        return Book.from_db_records(records)

    async def get_book_by_openlib_id(self, openlib_work_key: str = "") -> Record | None:
        result = await self.db.run_query("get_book_by_openlib_work_key", openlib_work_key=openlib_work_key)
        return Book.from_db_record(result)

    async def get_book_by_id(self, book_id: int) -> Record | None:
        result = await self.db.run_query("get_book_by_id", book_id=book_id)
        if result:
            return Book.from_db_record(result)
        return None

    async def get_books_by_author(self, author_id: int) -> list[Book]:
        records = await self.db.run_query("get_books_by_author", author_id=author_id)
        return Book.from_db_records(records)

    async def get_books_with_reviews_by_author(self, author_id: int) -> list[Book]:
        """Fetches books by an author and attaches their reviews."""
        books = await self.get_books_by_author(author_id)
        if not books:
            return []

        book_ids = [b.id for b in books]
        reviews = await self.review_repo.get_reviews_for_books(book_ids)
        reviews_by_book = defaultdict(list)

        for review in reviews:
            reviews_by_book[review.book_id].append(review)

        for book in books:
            book.reviews = reviews_by_book.get(book.id, [])

        return books

    """ search values """

    async def search_books(self, search_query: str):
        records = await self.db.run_query("search_books", search_query=search_query)
        return Book.from_db_records(records)

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
