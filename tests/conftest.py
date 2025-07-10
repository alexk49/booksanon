import pytest
from unittest.mock import AsyncMock
from datetime import datetime

from starlette.testclient import TestClient
from server.app import app


@pytest.fixture
def client():
    yield TestClient(app)


@pytest.fixture
def mock_db():
    class MockDB:
        run_query = AsyncMock()

    return MockDB()


@pytest.fixture
def mock_author_record():
    return {
        "id": 1,
        "name": "Mock Author",
        "remote_ids": {"openlibrary": "OL1A"},
        "openlib_id": "/authors/OL1A",
        "birth_date": "1970",
        "death_date": None,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }.copy()


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
    }.copy()


@pytest.fixture
def mock_review_record():
    def _review(review_id, book_id):
        return {
            "review_id": review_id,
            "book_id": book_id,
            "user_id": 42,
            "content": f"Review content {review_id}",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            # Book fields (used by Book.from_db_record)
            "title": "Mock Book",
            "authors": '[{"id": 1, "name": "Author One"}]',
            "author_names": ["Author One"],
            "author_keys": ["OL1A"],
            "openlib_work_key": "/works/OL123W",
            "cover_url": "http://example.com/cover.jpg",
            "subjects": ["fiction", "adventure"],
            "first_publish_year": 2000,
            "openlib_tags": ["fiction", "mock"],
            "publishers": ["Mock Publisher"],
            "isbns_13": ["9781234567890"],
            "isbns_10": ["1234567890"],
            "openlib_description": "A mock book description.",
            "openlib_cover_ids": ["1234", "5678"],
            "remote_links": '[{"title": "Sample Link", "url": "http://example.com"}]',
        }.copy()

    return _review
