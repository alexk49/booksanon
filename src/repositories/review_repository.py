from db import Database
from db.models import Book, Review


class ReviewRepository:
    def __init__(self, db: Database):
        self.db = db

    async def insert_review(self, user_id, book_id, review):
        return await self.db.run_query("insert_review", book_id=book_id, user_id=user_id, content=review)

    """ Get or read values """

    async def get_reviews_for_books(self, book_ids: list[int]) -> list[Review]:
        if not book_ids:
            return []
        records = await self.db.run_query("get_reviews_for_books", book_ids=book_ids)
        return [Review.from_db_record(r) for r in records]

    async def get_review_and_book_by_review_id(self, review_id: int):
        record = await self.db.run_query("get_review_and_book_by_review_id", review_id=review_id)
        return Review.from_db_record(record)

    async def get_most_recent_book_reviews(self, limit: int = 10) -> list[Book]:
        records = await self.db.run_query("get_most_recent_book_reviews", limit=limit)
        return Review.from_db_records(records)

    async def get_reviews_by_book_id(self, book_id: int) -> list[Book]:
        records = await self.db.run_query("get_reviews_by_book_id", book_id=book_id)
        return Review.from_db_records(records)
