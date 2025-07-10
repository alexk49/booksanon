import pytest

from db.models import Author
from repositories.author_repository import AuthorRepository


@pytest.fixture
def repo(mock_db):
    return AuthorRepository(mock_db)


@pytest.mark.asyncio
async def test_get_author_by_id_returns_author(repo, mock_db, monkeypatch):
    fake_record = {"id": 1, "name": "Author X"}
    mock_db.run_query.return_value = fake_record

    def mock_from_db_record(record):
        return Author(id=record["id"], name=record["name"])

    monkeypatch.setattr(Author, "from_db_record", mock_from_db_record)

    result = await repo.get_author_by_id(1)
    assert isinstance(result, Author)
    assert result.id == 1


@pytest.mark.asyncio
async def test_get_author_by_id_returns_none(repo, mock_db):
    mock_db.run_query.return_value = None
    result = await repo.get_author_by_id(1)
    assert result is None


@pytest.mark.asyncio
async def test_check_if_author_exists_true(repo, mock_db):
    mock_db.run_query.return_value = {"id": 42}
    result = await repo.check_if_author_exists("openlib123")
    assert result is True


@pytest.mark.asyncio
async def test_check_if_author_exists_false(repo, mock_db):
    mock_db.run_query.return_value = None
    result = await repo.check_if_author_exists("openlib123")
    assert result is False
