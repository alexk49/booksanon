import unittest
import asyncio
from unittest.mock import MagicMock, patch
from aiohttp.client_exceptions import ClientError

from client import Client


class TestClient(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.mock_session = MagicMock()

        self.client = Client(max_retries=3, retry_delay=0.1)
        self.client.session = self.mock_session

    async def test_fetch_results_success_first_attempt(self):
        """Test successful data fetch on the first attempt."""
        # Create a mock response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = MagicMock(return_value=asyncio.Future())
        mock_response.json.return_value.set_result({"data": "test_data"})

        # Set up the session.get to return our mock response
        self.mock_session.get = MagicMock(return_value=asyncio.Future())
        self.mock_session.get.return_value.set_result(mock_response)

        result = await self.client.fetch_results("https://test.com/api")

        self.mock_session.get.assert_called_once_with(
            "https://test.com/api", timeout=10
        )
        self.assertEqual(result, {"data": "test_data"})

    async def test_fetch_results_success_after_retry(self):
        """Test successful data fetch after one failed attempt."""
        fail_response = MagicMock()
        fail_response.status = 500

        success_response = MagicMock()
        success_response.status = 200
        success_response.json = MagicMock(return_value=asyncio.Future())
        success_response.json.return_value.set_result({"data": "retry_success"})

        # Set up the session.get to return mock responses in sequence
        self.mock_session.get = MagicMock(
            side_effect=[
                self._create_future(fail_response),
                self._create_future(success_response),
            ]
        )

        result = await self.client.fetch_results("https://test.com/api")

        self.assertEqual(self.mock_session.get.call_count, 2)
        self.assertEqual(result, {"data": "retry_success"})

    async def test_fetch_results_client_error_then_success(self):
        """Test recovery from a ClientError."""
        # Set up the session.get to first raise an error, then succeed
        success_response = MagicMock()
        success_response.status = 200
        success_response.json = MagicMock(return_value=asyncio.Future())
        success_response.json.return_value.set_result({"data": "error_recovery"})

        self.mock_session.get = MagicMock(
            side_effect=[
                ClientError("Connection error"),
                self._create_future(success_response),
            ]
        )

        result = await self.client.fetch_results("https://test.com/api")

        self.assertEqual(self.mock_session.get.call_count, 2)
        self.assertEqual(result, {"data": "error_recovery"})

    async def test_fetch_results_all_attempts_fail(self):
        """Test when all retry attempts fail."""
        # Set up the session.get to always raise an error
        self.mock_session.get = MagicMock(side_effect=ClientError("Persistent error"))

        result = await self.client.fetch_results("https://test.com/api")

        self.assertEqual(self.mock_session.get.call_count, 3)
        self.assertIsNone(result)

    async def test_fetch_results_non_200_responses(self):
        """Test when all responses return non-200 status codes."""
        # Create mock responses - all return error status codes
        error_response = MagicMock()
        error_response.status = 404

        # Set up the session.get to return error responses
        self.mock_session.get = MagicMock(
            return_value=self._create_future(error_response)
        )

        result = await self.client.fetch_results("https://test.com/api")

        self.assertEqual(self.mock_session.get.call_count, 3)
        self.assertIsNone(result)

    async def test_semaphore_usage(self):
        """Test that the semaphore is properly acquired and released."""
        # Replace the actual semaphore with a mock
        self.client.semaphore = MagicMock()
        self.client.semaphore.__aenter__ = MagicMock(return_value=asyncio.Future())
        self.client.semaphore.__aenter__.return_value.set_result(None)
        self.client.semaphore.__aexit__ = MagicMock(return_value=asyncio.Future())
        self.client.semaphore.__aexit__.return_value.set_result(None)

        # Create a mock response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = MagicMock(return_value=asyncio.Future())
        mock_response.json.return_value.set_result({"data": "test_data"})

        self.mock_session.get = MagicMock(return_value=asyncio.Future())
        self.mock_session.get.return_value.set_result(mock_response)

        await self.client.fetch_results("https://test.com/api")

        self.client.semaphore.__aenter__.assert_called_once()
        self.client.semaphore.__aexit__.assert_called_once()

    @patch("aiohttp.ClientSession")
    async def test_create_session_when_none(self, mock_client_session):
        """Test creating a new session when none exists."""
        # Setup clean client with no session
        self.client.session = None
        self.client.email = "test@example.com"
        
        # Mock ClientSession
        mock_session_instance = MagicMock()
        mock_client_session.return_value = mock_session_instance
        
        # Call create_session
        await self.client.create_session()
        
        # Verify session was created with correct headers
        mock_client_session.assert_called_once_with(
            headers={"User-Agent": "booksanon test@example.com"}
        )
        self.assertEqual(self.client.session, mock_session_instance)

    @patch("aiohttp.ClientSession")
    async def test_create_session_when_exists(self, mock_client_session):
        """Test that create_session doesn't recreate an existing session."""
        existing_session = MagicMock()
        self.client.session = existing_session
        
        await self.client.create_session()
        
        mock_client_session.assert_not_called()
        self.assertEqual(self.client.session, existing_session)

    async def test_close_session_when_exists(self):
        """Test closing an existing session."""
        mock_session = MagicMock()
        mock_session.close = MagicMock(return_value=asyncio.Future())
        mock_session.close.return_value.set_result(None)
        self.client.session = mock_session
        
        await self.client.close_session()
        
        mock_session.close.assert_called_once()
        self.assertIsNone(self.client.session)

    async def test_close_session_when_none(self):
        """Test that close_session handles a None session gracefully."""
        self.client.session = None
        
        await self.client.close_session()
        
        self.assertIsNone(self.client.session)

    async def test_init_parameters(self):
        """Test that initialization parameters are stored correctly."""
        client = Client(
            max_concurrent_requests=5,
            max_retries=4,
            retry_delay=2,
            email="user@example.com"
        )
        
        # Verify parameters were stored
        self.assertEqual(client.max_retries, 4)
        self.assertEqual(client.retry_delay, 2)
        self.assertEqual(client.email, "user@example.com")
        self.assertIsInstance(client.semaphore, asyncio.Semaphore)
        # Test semaphore value (this is implementation-dependent but works in CPython)
        self.assertEqual(client.semaphore._value, 5)
        self.assertIsNone(client.session)

    def _create_future(self, result):
        """Helper method to create a completed future with the given result."""
        future = asyncio.Future()
        future.set_result(result)
        return future


if __name__ == "__main__":
    unittest.main()
