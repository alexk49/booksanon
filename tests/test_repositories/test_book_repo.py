from unittest.mock import AsyncMock
import pytest
from db.models.book import Book
from db.models.review import Review

from repositories.book_repository import BookRepository


@pytest.fixture
def mock_review_repo():
    class MockReviewRepo:
        get_reviews_for_books = AsyncMock()

    return MockReviewRepo()


@pytest.fixture
def repo(mock_db, mock_review_repo):
    return BookRepository(mock_db, mock_review_repo)


@pytest.mark.asyncio
async def test_get_book_and_reviews_by_book_id(repo, mock_db, mock_book_record, mock_review_record):
    # Simulate DB joined rows: book + reviews
    record1 = {**mock_book_record, **mock_review_record(book_id=1, review_id=10)}
    record2 = {**mock_book_record, **mock_review_record(book_id=1, review_id=11)}
    mock_db.run_query.return_value = [record1, record2]

    # Patch Review.from_joined_record to parse mock record correctly
    def patched_from_joined_record(r):
        return Review(
            id=r["review_id"],
            book_id=r["id"],
            user_id=r["user_id"],
            content=r["content"],
            created_at=r["created_at"],
            updated_at=r["updated_at"],
        )

    Review.from_joined_record = patched_from_joined_record

    # Patch Book.from_db_record if needed (optional)
    Book.from_db_record = lambda r: Book(
        id=r["id"],
        title=r["title"],
        authors=r["authors"],
        author_keys=r["author_keys"],
        author_names=r["author_names"],
        first_publish_year=r["first_publish_year"],
        openlib_work_key=r["openlibrary_key"],
        created_at=r["created_at"],
        updated_at=r["updated_at"],
    )

    result_book, reviews = await repo.get_book_and_reviews_by_book_id(book_id=1)

    assert result_book.id == 1
    assert result_book.title == "Mock Book"
    assert len(reviews) == 2
    assert reviews[0].id == 10
    assert reviews[1].id == 11
    assert reviews[0].content == "Review content 10"
