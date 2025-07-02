import pytest
from repositories.user_repository import UserRepository


@pytest.mark.asyncio
async def test_create_anon(mock_db):
    repo = UserRepository(mock_db)

    await repo.create_anon()
    mock_db.run_query.assert_called_once_with("create_anon")


@pytest.mark.asyncio
async def test_get_user_id_by_username_found(mock_db):
    repo = UserRepository(mock_db)

    mock_db.run_query.return_value = {"id": 42}
    result = await repo.get_user_id_by_username("jdoe")

    mock_db.run_query.assert_called_once_with("get_user_id_by_username", username="jdoe")
    assert result == 42


@pytest.mark.asyncio
async def test_get_user_id_by_username_not_found(mock_db):
    repo = UserRepository(mock_db)

    mock_db.run_query.return_value = None
    result = await repo.get_user_id_by_username("ghost")

    mock_db.run_query.assert_called_once_with("get_user_id_by_username", username="ghost")
    assert result is None
