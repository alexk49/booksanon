"""
httpx client for making async api calls
"""

import asyncio
import logging
import httpx

from typing import Optional

logger = logging.getLogger("app.calls")

class Client:
    def __init__(
        self,
        max_retries=3,
        retry_delay=5,
        timeout=10,
        email="",
    ) -> None:
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.timeout = httpx.Timeout(timeout, connect=5.0, read=5.0, write=5.0)
        self.session: Optional[httpx.AsyncClient] = None
        self.email = email
        self.headers = {"User-Agent": f"booksanon {self.email}"}

    async def start_session(self) -> httpx.AsyncClient:
        if self.session is None:
            self.session = httpx.AsyncClient(headers=self.headers, timeout=self.timeout)
        return self.session

    async def close_session(self) -> None:
        if self.session:
            await self.session.aclose()
            self.session = None

    async def __aenter__(self):
        self.session = httpx.AsyncClient(headers=self.headers)
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.session.aclose()

    async def fetch_results(self, url: str, params: dict = {}):
        self.session = await self.start_session()

        logger.info(f"making request to %s, with %s", url, params)
        for attempt in range(1, self.max_retries + 1):
            try:
                if params != {}:
                    response = await self.session.get(url, params=params)
                else:
                    response = await self.session.get(url)

                if response.status_code == 200:
                    return response.json()

                logger.info(f"Attempt {attempt}: Received status {response.status_code}, {response}")
            except httpx.HTTPError as exc:
                logger.warning(f"HTTP Exception on attempt: {attempt} for {exc.request.url} - {exc}")

            if attempt < self.max_retries:
                await asyncio.sleep(self.retry_delay)

        logger.warning(f"Failed to fetch data from {url}, after {self.max_retries} attempts")
        return None
