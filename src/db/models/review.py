from dataclasses import dataclass
from typing import Optional

from asyncpg import Record

from .book import Book
from .utils import make_json_safe


@dataclass
class Review:
    id: int
    book_id: int
    user_id: int
    content: str
    updated_at: str
    created_at: str
    book: Optional[Book] = None

    @classmethod
    def from_db_record(cls, record: Record) -> "Review":
        book_data = Book.from_db_record(record)
        return cls(
            id=record.get("review_id"),
            book_id=record.get("book_id"),
            user_id=record.get("user_id"),
            content=record.get("content"),
            updated_at=record.get("updated_at"),
            created_at=record.get("created_at"),
            book=book_data,
        )

    @classmethod
    def from_db_records(cls, records: list[Record]) -> list["Review"]:
        return [cls.from_db_record(r) for r in records]

    @classmethod
    def from_joined_record(cls, record: Record) -> "Review":
        return cls(
            id=record.get("review_id"),
            book_id=record.get("book_id"),
            user_id=record.get("user_id"),
            content=record.get("content"),
            created_at=record.get("created_at"),
            updated_at=record.get("updated_at"),
        )

    def to_json_dict(self) -> dict:
        if self.book:
            self.book = make_json_safe(self.book)
        return make_json_safe(self)
