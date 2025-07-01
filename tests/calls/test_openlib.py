import asyncio
import pytest

from unittest.mock import AsyncMock, patch, MagicMock

from calls.client import Client
from calls.openlib import OpenLibCaller


@pytest.fixture
async def openlib_caller():
    client = Client(max_retries=3, retry_delay=0.1)
    caller = OpenLibCaller(client=client, max_concurrent_requests=2)

    yield caller

    await client.close_session()


async def test_semaphore_limits_concurrency(openlib_caller: OpenLibCaller):
    in_flight_counter = [0]
    max_in_flight = [0]

    async def fake_request(*args, **kwargs):
        in_flight_counter[0] += 1
        max_in_flight[0] = max(max_in_flight[0], in_flight_counter[0])

        await asyncio.sleep(0.1)

        in_flight_counter[0] -= 1

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"ok": True}
        return mock_resp

    with patch("calls.client.Client.fetch_results", new=AsyncMock(side_effect=fake_request)):
        urls = [f"https://fakeurl.com/{i}" for i in range(5)]

        tasks = [openlib_caller.fetch_with_semaphore(url) for url in urls]
        await asyncio.gather(*tasks)

        assert max_in_flight[0] <= 2
        assert max_in_flight[0] == 2
