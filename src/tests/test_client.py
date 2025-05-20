import unittest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock

from client import Client


class TestClient(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.test_url = "https://example.com"
        self.client = Client(max_concurrent_requests=2, max_retries=3, retry_delay=0.1)

    async def asyncTearDown(self):
        await self.client.close_session()

    @patch("httpx.AsyncClient.get")
    async def test_fetch_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "ok"}
        mock_get.return_value = mock_response

        result = await self.client.fetch_results(self.test_url)

        self.assertEqual(result, {"data": "ok"})
        self.assertEqual(mock_get.call_count, 1)

    @patch("httpx.AsyncClient.get")
    async def test_fetch_retries_on_failure(self, mock_get):
        fail_response = MagicMock()
        fail_response.status_code = 500

        success_response = MagicMock()
        success_response.status_code = 200
        success_response.json.return_value = {"success": True}

        mock_get.side_effect = [fail_response, fail_response, success_response]

        result = await self.client.fetch_results(self.test_url)

        self.assertEqual(result, {"success": True})
        self.assertEqual(mock_get.call_count, 3)

    @patch("httpx.AsyncClient.get")
    async def test_fetch_gives_up_after_max_retries(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        result = await self.client.fetch_results(self.test_url)

        self.assertIsNone(result)
        self.assertEqual(mock_get.call_count, self.client.max_retries)

    async def test_session_context_manager(self):
        async with Client(email="test@example.com") as client:
            self.assertIsNotNone(client.session)
            self.assertTrue(hasattr(client.session, "get"))
            self.assertEqual(
                client.session.headers["User-Agent"], "booksanon test@example.com"
            )

    async def test_semaphore_limits_concurrency(self):
        # Tests that at most 2 requests run concurrently
        in_flight = 0
        max_in_flight = 0

        async def fake_request(*args, **kwargs):
            nonlocal in_flight, max_in_flight
            in_flight += 1
            max_in_flight = max(max_in_flight, in_flight)
            await asyncio.sleep(0.1)
            in_flight -= 1
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {"ok": True}
            return mock_resp

        with patch("httpx.AsyncClient.get", new=AsyncMock(side_effect=fake_request)):
            urls = [self.test_url] * 5
            tasks = [self.client.fetch_results(url) for url in urls]
            await asyncio.gather(*tasks)

            self.assertLessEqual(max_in_flight, 2)  # max_concurrent_requests


if __name__ == "__main__":
    unittest.main()
