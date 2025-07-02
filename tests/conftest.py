import pytest
from unittest.mock import AsyncMock
from datetime import datetime


@pytest.fixture
def mock_db():
    class MockDB:
        run_query = AsyncMock()

    return MockDB()


@pytest.fixture
def mock_book_record():
    return {
        "id": 1,
        "title": "Mock Book",
        "authors": '[{"id": 1, "name": "Author One"}]',
        "author_keys": ["OL1A"],
        "author_names": ["Author One"],
        "cover_url": "http://example.com/cover.jpg",
        "description": "Sample description",
        "subjects": ["fiction", "adventure"],
        "first_publish_year": 2000,
        "openlibrary_key": "OL123M",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }


@pytest.fixture
def mock_review_record():
    def _review(book_id, review_id):
        return {
            "id": book_id,
            "review_id": review_id,
            "user_id": 42,
            "content": f"Review content {review_id}",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

    return _review
