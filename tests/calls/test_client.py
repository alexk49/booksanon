import pytest
from unittest.mock import MagicMock

from calls.client import Client


TEST_URL = "https://example.com"


@pytest.fixture
async def client():
    client = Client(max_retries=3, retry_delay=0.1)
    yield client

    await client.close_session()


async def test_fetch_success(client: Client, mocker):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": "ok"}

    mock_get = mock_response
    mock_get = mocker.patch("httpx.AsyncClient.get", return_value=mock_response)

    result = await client.fetch_results(TEST_URL)

    assert result == {"data": "ok"}
    mock_get.assert_called_once_with(TEST_URL)


async def test_fetch_retries_on_failure(client, mocker):
    fail_response = MagicMock()
    fail_response.status_code = 500

    success_response = MagicMock()
    success_response.status_code = 200
    success_response.json.return_value = {"success": True}

    mock_get = mocker.patch("httpx.AsyncClient.get", side_effect=[fail_response, fail_response, success_response])

    result = await client.fetch_results(TEST_URL)

    assert result == {"success": True}
    assert mock_get.call_count == 3


async def test_fetch_gives_up_after_max_retries(client, mocker):
    mock_response = MagicMock()
    mock_response.status_code = 500

    mock_get = mocker.patch("httpx.AsyncClient.get", return_value=mock_response)

    result = await client.fetch_results(TEST_URL)

    assert result is None
    assert mock_get.call_count == client.max_retries


async def test_session_context_manager():
    async with Client(email="test@example.com") as client:
        assert client.session is not None
        assert hasattr(client.session, "get")
        assert client.session.headers["User-Agent"] == "booksanon test@example.com"
