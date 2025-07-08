import pytest
from unittest.mock import AsyncMock

from db.models import Author, Book, Review
from server.form_validators import search_form_fields
from server.resources import resources


def mock_validate_csrf_token(session_token, form_token):
    return {"ok": True, "value": form_token}


@pytest.fixture
def mock_book_repo(monkeypatch, mock_book_record):
    # Mock for `get_book_and_reviews_by_book_id`
    mock_get_book_and_reviews = AsyncMock()
    book = Book.from_db_record(mock_book_record)
    mock_get_book_and_reviews.return_value = (book, [])  # empty reviews here is fine

    monkeypatch.setattr(resources.book_repo, "get_book_and_reviews_by_book_id", mock_get_book_and_reviews)

    # Mock for `get_books_with_reviews_by_author`
    mock_get_books_by_author = AsyncMock()
    mock_get_books_by_author.return_value = [book]
    monkeypatch.setattr(resources.book_repo, "get_books_with_reviews_by_author", mock_get_books_by_author)

    mock_search_books = AsyncMock()
    mock_search_books.return_value = [book]
    monkeypatch.setattr(resources.book_repo, "search_books", mock_search_books)

    return {
        "get_book_and_reviews_by_book_id": mock_get_book_and_reviews,
        "get_books_with_reviews_by_author": mock_get_books_by_author,
        "search_books": mock_search_books,
    }


@pytest.fixture
def mock_author_repo(monkeypatch, mock_author_record):
    async_mock = AsyncMock()
    author = Author.from_db_record(mock_author_record)
    async_mock.return_value = author
    monkeypatch.setattr(resources.author_repo, "get_author_by_id", async_mock)
    return async_mock


@pytest.fixture
def mock_review_repo(monkeypatch):
    async_mock = AsyncMock()
    monkeypatch.setattr(resources.review_repo, "get_most_recent_book_reviews", async_mock)
    monkeypatch.setattr(resources.review_repo, "get_review_and_book_by_review_id", async_mock)
    return async_mock


def test_home(client, mock_review_repo, mock_review_record):
    review = Review.from_db_record(mock_review_record(1, 101))
    mock_review_repo.return_value = [review]
    response = client.get("/")
    assert response.status_code == 200
    assert "Mock Book" in response.text


def test_add_book(client):
    response = client.get("/add-book")
    assert response.status_code == 200


def test_submission(client):
    response = client.get("/submission")
    assert response.status_code == 200


def test_review_page(client, mock_review_repo, mock_review_record):
    review = Review.from_db_record(mock_review_record(1, 101))
    mock_review_repo.return_value = review
    response = client.get("/review/1")
    assert response.status_code == 200
    assert "Review content" in response.text


def test_book_page(client, mock_book_repo):
    response = client.get("/book/1")
    assert response.status_code == 200


def test_author_page(client, mock_book_repo, mock_author_repo):
    response = client.get("/author/1")
    assert response.status_code == 200
    assert "Mock Author" in response.text
    assert "Mock Book" in response.text


def test_search_get_with_query(client, mock_book_repo):
    response = client.get("/search?q=Mock+Book")
    assert response.status_code == 200
    assert b"Mock Book" in response.content

    mock_book_repo["search_books"].assert_called_once_with(search_query="Mock Book")


def test_search_get_without_query(client, mock_book_repo):
    response = client.get("/search")
    assert response.status_code == 200
    assert b"No results" in response.content or b"Mock Book" not in response.content


def test_search_post_redirect(client, mock_review_repo, mock_review_record, mock_book_repo):
    review = Review.from_db_record(mock_review_record(1, 101))
    mock_review_repo.return_value = [review]

    client.get("/")
    csrf_response = client.get("/api/csrf-token")
    csrf_token = csrf_response.json()["csrf_token"]

    search_form_fields["csrf_token"] = [mock_validate_csrf_token]

    response = client.post(
        "/search",
        data={"search_query": "Mock Book", "csrf_token": csrf_token},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == 200
    assert "/search?q=Mock+Book" in str(response.url)
