import pytest
from unittest.mock import MagicMock, patch
from dataclasses import asdict
import json

from db.models.book import Book


@pytest.fixture
def book_data():
    return {
        "title": "Test Book",
        "author_names": ["Test Author"],
        "author_keys": ["/authors/OL12345A"],
        "first_publish_year": "2023",
        "openlib_work_key": "/works/OL12345W",
        "cover_id": "12345",
        "covers": ["12345", "67890"],
        "description": {"value": "A test book."},
        "subjects": ["fiction", "testing"],
        "links": [{"title": "Goodreads", "url": "https://www.goodreads.com/book/show/12345"}],
        "number_of_pages_median": 300,
        "isbns_13": ["978-0321765723"],
        "isbns_10": ["0321765723"],
        "publishers": ["Test Publisher"],
    }


@pytest.fixture
def db_record():
    record = MagicMock()
    record.get.side_effect = lambda key, default=None: {
        "book_id": 1,
        "title": "DB Book",
        "authors": json.dumps([{"id": 1, "name": "DB Author"}]),
        "author_names": ["DB Author"],
        "author_keys": ["/authors/OL67890A"],
        "openlib_work_key": "/works/OL67890W",
        "publishers": ["DB Publisher"],
        "isbns_13": ["978-0321765723"],
        "isbns_10": ["0321765723"],
        "openlib_cover_ids": ["67890", "12345"],
        "number_of_pages_median": 400,
        "openlib_description": "A book from the database.",
        "openlib_tags": ["db", "testing"],
        "remote_links": json.dumps([{"title": "LibraryThing", "url": "https://www.librarything.com/work/12345"}]),
        "first_publish_year": "2022",
        "created_at": "2022-01-01T00:00:00",
        "updated_at": "2022-01-01T00:00:00",
    }.get(key, default)
    return record


def test_book_creation():
    book = Book(title="New Book", openlib_work_key="/works/OL1W", author_names=["Author"], author_keys=["/a/1"])
    assert book.title == "New Book"
    assert book.openlib_tags == set()


def test_from_dict(book_data):
    book = Book.from_dict(book_data)
    assert book.title == "Test Book"
    assert book.openlib_description == "A test book."
    assert "fiction" in book.openlib_tags


def test_to_db_dict():
    book = Book(title="Another Book", openlib_work_key="/works/OL2W", author_names=["Author"], author_keys=["/a/2"])
    with patch("db.models.book.map_types_for_db", side_effect=lambda d: d) as mock_map:
        db_dict = book.to_db_dict()
        mock_map.assert_called_once()
        expected_dict = asdict(book)
        assert db_dict == expected_dict


def test_from_db_record(db_record):
    book = Book.from_db_record(db_record)
    assert book.id == 1
    assert book.title == "DB Book"
    assert len(book.authors) == 1
    assert book.authors[0].name == "DB Author"
    assert "db" in book.openlib_tags


def test_author_display():
    book = Book(
        title="A Book",
        openlib_work_key="/works/OL3W",
        author_names=["Author A", "Author B"],
        author_keys=["/a/3", "/a/4"],
    )
    assert book.author_display == "Author A, Author B"


def test_tags_display():
    book = Book(
        title="A Book",
        openlib_work_key="/works/OL3W",
        author_names=["Author"],
        author_keys=["/a/1"],
        openlib_tags={"c", "a", "b"},
    )
    assert book.tags_display == ["a", "b", "c"]


def test_publishers_display():
    book = Book(
        title="A Book",
        openlib_work_key="/works/OL3W",
        author_names=["Author"],
        author_keys=["/a/1"],
        publishers={"c", "a", "b"},
    )
    assert book.publishers_display == ["a", "b", "c"]


def test_link_outs():
    book = Book(title="A Book", openlib_work_key="/works/OL3W", author_names=["Author"], author_keys=["/a/1"])
    links = book.link_outs
    assert any("OpenLibrary" in link["text"] for link in links)
    assert any("bookshop.org" in link["url"] for link in links)
