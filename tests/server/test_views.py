import pytest
from unittest.mock import AsyncMock, Mock

from db.models import Author, Book, Review
from server.form_validators import book_submit_fields, search_form_fields
from server.resources import resources


def mock_validate_csrf_token(session_token, form_token):
    return {"ok": True, "value": form_token}


@pytest.fixture
def mock_book_repo(monkeypatch, mock_book_record):
    mock_get_book_and_reviews = AsyncMock()
    book = Book.from_db_record(mock_book_record)
    mock_get_book_and_reviews.return_value = (book, [])

    monkeypatch.setattr(resources.book_repo, "get_book_and_reviews_by_book_id", mock_get_book_and_reviews)

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
    mock_get_recent = AsyncMock()
    mock_get_by_id = AsyncMock()
    monkeypatch.setattr(resources.review_repo, "get_most_recent_book_reviews", mock_get_recent)
    monkeypatch.setattr(resources.review_repo, "get_review_and_book_by_review_id", mock_get_by_id)
    return {
        "get_most_recent_book_reviews": mock_get_recent,
        "get_review_and_book_by_review_id": mock_get_by_id,
    }


@pytest.fixture
def mock_openlib_caller(monkeypatch):
    async_mock = AsyncMock()
    monkeypatch.setattr(resources.openlib_caller, "search_books", async_mock)
    return async_mock


@pytest.fixture
def mock_queue_repo(monkeypatch):
    async_mock = AsyncMock()
    monkeypatch.setattr(resources.queue_repo, "insert_review_submission", async_mock)
    return async_mock


@pytest.fixture
def mock_process_review_submission(monkeypatch):
    mock = Mock()
    monkeypatch.setattr("server.views.process_review_submission", mock)
    return mock


def test_home(client, mock_review_repo, mock_review_record):
    review_record = mock_review_record(1, 101)
    review = Review.from_db_record(review_record)
    mock_review_repo["get_most_recent_book_reviews"].return_value = [review]
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
    mock_review_repo["get_review_and_book_by_review_id"].return_value = review
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
    mock_review_repo["get_most_recent_book_reviews"].return_value = [review]

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


def test_search_api(client, mock_book_repo, mock_book_record, mock_review_repo):
    mock_review_repo["get_most_recent_book_reviews"].return_value = []
    client.get("/")
    csrf_response = client.get("/api/csrf-token")
    csrf_token = csrf_response.json()["csrf_token"]

    search_form_fields["csrf_token"] = [mock_validate_csrf_token]

    response = client.post(
        "/api/search",
        data={"search_query": "Mock Book", "csrf_token": csrf_token},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == 200
    json_response = response.json()
    assert json_response["success"] is True
    assert len(json_response["results"]) == 1
    assert json_response["results"][0]["title"] == "Mock Book"
    mock_book_repo["search_books"].assert_called_once_with(search_query="Mock Book")


def test_search_openlib(client, mock_openlib_caller, mock_review_repo):
    mock_review_repo["get_most_recent_book_reviews"].return_value = []
    client.get("/")
    csrf_response = client.get("/api/csrf-token")
    csrf_token = csrf_response.json()["csrf_token"]

    search_form_fields["csrf_token"] = [mock_validate_csrf_token]
    mock_openlib_caller.return_value = [
        {
            "title": "Test Book",
            "author_names": ["Test Author"],
            "author_keys": ["OL1A"],
            "cover_i": 123,
            "openlib_id": "OL1M",
            "first_publish_year": 2021,
            "openlib_work_key": "OL1W",
        }
    ]

    response = client.post(
        "/api/search-openlib",
        data={"search_query": "Test Book", "csrf_token": csrf_token},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == 200
    json_response = response.json()
    assert json_response["success"] is True
    assert len(json_response["results"]) == 1
    assert json_response["results"][0]["title"] == "Test Book"
    mock_openlib_caller.assert_called_once_with(search_query="Test Book", limit=10)


def test_submit_book(client, mock_queue_repo, mock_process_review_submission, mock_review_repo):
    mock_review_repo["get_most_recent_book_reviews"].return_value = []
    client.get("/")
    csrf_response = client.get("/api/csrf-token")
    csrf_token = csrf_response.json()["csrf_token"]

    book_submit_fields["csrf_token"] = [mock_validate_csrf_token]
    mock_queue_repo.return_value = 1

    response = client.post(
        "/api/submit-book",
        data={
            "openlib_id_hidden": "OL1W",
            "review": "This is a test review.",
            "csrf_token": csrf_token,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == 200
    json_response = response.json()
    assert json_response["success"] is True
    assert json_response["message"] == "Thanks for adding a review! Your submission is being processed."
    assert json_response["submission_id"] == 1
    mock_queue_repo.assert_called_once_with(openlib_id="OL1W", review="This is a test review.")
    mock_process_review_submission.assert_called_once_with(1)


def test_set_csrf_token(client):
    response = client.get("/api/csrf-token")
    assert response.status_code == 200
    json_response = response.json()
    assert "csrf_token" in json_response
    assert isinstance(json_response["csrf_token"], str)
    assert len(json_response["csrf_token"]) > 10
