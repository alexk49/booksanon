import pytest
from unittest.mock import MagicMock, patch
from dataclasses import asdict

from db.models.author import Author


@pytest.fixture
def author_data():
    return {
        "name": "Test Author",
        "death_date": "2023-01-01",
        "birth_date": "2000-01-01",
        "key": "/authors/OL12345A",
        "remote_ids": {"librarything": "12345"},
    }


@pytest.fixture
def db_record():
    record = MagicMock()
    record.get.side_effect = lambda key: {
        "id": 1,
        "name": "DB Author",
        "remote_ids": {"goodreads": "67890"},
        "openlib_id": "/authors/OL67890A",
        "birth_date": "1990-01-01",
        "death_date": "2020-01-01",
        "created_at": "2022-01-01T00:00:00",
        "updated_at": "2022-01-01T00:00:00",
    }.get(key)
    return record


def test_author_creation():
    author = Author(name="New Author")
    assert author.name == "New Author"
    assert author.remote_ids == {}
    assert author.id is None


def test_from_dict(author_data):
    author = Author.from_dict(author_data)
    assert author.name == "Test Author"
    assert author.openlib_id == "/authors/OL12345A"
    assert author.remote_ids == {"librarything": "12345"}


def test_to_db_dict():
    author = Author(name="Another Author", openlib_id="OL54321A")
    with patch("db.models.author.map_types_for_db", side_effect=lambda d: d) as mock_map:
        db_dict = author.to_db_dict()
        mock_map.assert_called_once()
        expected_dict = asdict(author)
        assert db_dict == expected_dict


def test_from_db_record(db_record):
    author = Author.from_db_record(db_record)
    assert author.id == 1
    assert author.name == "DB Author"
    assert author.openlib_id == "/authors/OL67890A"
    assert author.remote_ids == {"goodreads": "67890"}
