import pytest
from db.models.review import Review
from repositories.review_repository import ReviewRepository


@pytest.mark.asyncio
async def test_insert_review(mock_db):
    repo = ReviewRepository(mock_db)

    mock_db.run_query.return_value = 1  # Simulate insert success (e.g. inserted ID)
    result = await repo.insert_review(user_id=1, book_id=2, review="Nice read!")

    mock_db.run_query.assert_called_once_with("insert_review", book_id=2, user_id=1, content="Nice read!")
    assert result == 1


@pytest.mark.asyncio
async def test_get_reviews_for_books(mock_db, mock_review_record, monkeypatch):
    repo = ReviewRepository(mock_db)

    record1 = mock_review_record(book_id=1, review_id=101)
    record2 = mock_review_record(book_id=2, review_id=102)
    mock_db.run_query.return_value = [record1, record2]

    def mock_from_db_record(r):
        return Review(
            id=r["review_id"],
            book_id=r["book_id"],
            user_id=r["user_id"],
            content=r["content"],
            created_at=r["created_at"],
            updated_at=r["updated_at"],
        )

    monkeypatch.setattr(Review, "from_db_record", mock_from_db_record)

    reviews = await repo.get_reviews_for_books([1, 2])

    assert len(reviews) == 2
    assert reviews[0].id == 101
    assert reviews[1].book_id == 2


@pytest.mark.asyncio
async def test_get_reviews_for_books_empty_list(mock_db):
    repo = ReviewRepository(mock_db)
    reviews = await repo.get_reviews_for_books([])
    assert reviews == []


@pytest.mark.asyncio
async def test_get_review_and_book_by_review_id(mock_db, mock_review_record, monkeypatch):
    repo = ReviewRepository(mock_db)
    record = mock_review_record(book_id=3, review_id=300)
    mock_db.run_query.return_value = record

    def mock_from_db_record(r):
        return Review(
            id=r["review_id"],
            book_id=r["book_id"],
            user_id=r["user_id"],
            content=r["content"],
            created_at=r["created_at"],
            updated_at=r["updated_at"],
        )

    monkeypatch.setattr(Review, "from_db_record", mock_from_db_record)

    review = await repo.get_review_and_book_by_review_id(300)
    assert review.id == 300
    assert review.book_id == 3


@pytest.mark.asyncio
async def test_get_most_recent_book_reviews(mock_db, mock_review_record, monkeypatch):
    repo = ReviewRepository(mock_db)
    mock_records = [mock_review_record(book_id=1, review_id=i) for i in range(5)]
    mock_db.run_query.return_value = mock_records

    def mock_from_db_records(records):
        return [
            Review(
                id=r["review_id"],
                book_id=r["book_id"],
                user_id=r["user_id"],
                content=r["content"],
                created_at=r["created_at"],
                updated_at=r["updated_at"],
            )
            for r in records
        ]

    monkeypatch.setattr(Review, "from_db_records", mock_from_db_records)

    reviews = await repo.get_most_recent_book_reviews(limit=5)
    assert len(reviews) == 5
    assert reviews[0].id == 0
    assert reviews[-1].id == 4


@pytest.mark.asyncio
async def test_get_reviews_by_book_id(mock_db, mock_review_record, monkeypatch):
    repo = ReviewRepository(mock_db)
    mock_records = [mock_review_record(book_id=42, review_id=i) for i in range(3)]
    mock_db.run_query.return_value = mock_records

    def mock_from_db_records(records):
        return [
            Review(
                id=r["review_id"],
                book_id=r["book_id"],
                user_id=r["user_id"],
                content=r["content"],
                created_at=r["created_at"],
                updated_at=r["updated_at"],
            )
            for r in records
        ]

    monkeypatch.setattr(Review, "from_db_records", mock_from_db_records)

    reviews = await repo.get_reviews_by_book_id(book_id=42)
    assert all(r.book_id == 42 for r in reviews)
    assert len(reviews) == 3
