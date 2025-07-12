import pytest
from unittest.mock import MagicMock
import json

from db.models.review import Review
from db.models.book import Book


@pytest.fixture
def review_record():
    record = MagicMock()
    record.get.side_effect = lambda key, default=None: {
        "review_id": 1,
        "book_id": 1,
        "user_id": 1,
        "content": "A great book!",
        "created_at": "2022-01-01T00:00:00",
        "updated_at": "2022-01-01T00:00:00",
        # Book data for from_db_record
        "title": "DB Book",
        "authors": json.dumps([{"id": 1, "name": "DB Author"}]),
        "author_names": ["DB Author"],
        "author_keys": ["/authors/OL67890A"],
        "openlib_work_key": "/works/OL67890W",
    }.get(key, default)
    return record


def test_review_creation():
    review = Review(id=1, book_id=1, user_id=1, content="Test", created_at="now", updated_at="now")
    assert review.id == 1
    assert review.content == "Test"


def test_from_db_record(review_record):
    review = Review.from_db_record(review_record)
    assert review.id == 1
    assert review.content == "A great book!"
    assert isinstance(review.book, Book)
    assert review.book.title == "DB Book"


def test_from_joined_record(review_record):
    review = Review.from_joined_record(review_record)
    assert review.id == 1
    assert review.content == "A great book!"
    assert review.book is None


def test_from_db_records(review_record):
    reviews = Review.from_db_records([review_record, review_record])
    assert len(reviews) == 2
    assert reviews[0].id == 1
