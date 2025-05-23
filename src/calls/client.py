"""
httpx client for making async api calls
"""

import asyncio
import httpx


class Client:
    def __init__(
        self,
        max_concurrent_requests=5,
        max_retries=3,
        retry_delay=5,
        timeout=10,
        email="",
    ) -> None:
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.semaphore = asyncio.Semaphore(max_concurrent_requests)
        self.timeout = httpx.Timeout(timeout, connect=5.0, read=5.0, write=5.0)

        self.session = None
        self.email = email
        self.headers = {}
        # self.headers = {"User-Agent": f"booksanon {self.email}"}

    async def start_session(self) -> None:
        if self.session is None:
            self.session = httpx.AsyncClient(headers=self.headers, timeout=self.timeout)

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
        await self.start_session()

        print(f"making request to {url}, with {params}")
        for attempt in range(1, self.max_retries + 1):
            try:
                async with self.semaphore:
                    if params != {}:
                        response = await self.session.get(url, params=params)
                    else:
                        response = await self.session.get(url)

                    if response.status_code == 200:
                        return response.json()

                    print(f"Attempt {attempt}: Received status {response.status_code}")
            except httpx.HTTPError as exc:
                print(f"HTTP Exception on attempt: {attempt} for {exc.request.url} - {exc}")

            if attempt < self.max_retries:
                await asyncio.sleep(self.retry_delay)

        print(f"Failed to fetch data from {url}, after {self.max_retries} attempts")
        return None
