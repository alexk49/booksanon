"""
Async Client for making async API calls
"""
import aiohttp
import asyncio


class Client:
    """
    Async api client for making requests

    Can either be used with manual open/close session:
    >>> client = Client(email=EMAIL_ADDRESS)
    >>> await client.create_session()
    >>> results = await client.fetch_results(url)
    >>> print(results)
    >>> await client.close_session()

    Or with context manager:
    >>> async with Client(email=EMAIL_ADDRESS) as client:
    >>>    results = await client.fetch_results(url)
    >>>    print(results)
    """

    def __init__(self, max_concurrent_requests=3, max_retries=3, retry_delay=3, email="") -> None:
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.semaphore = asyncio.Semaphore(max_concurrent_requests)
        self.session = None
        self.email = email

    async def create_session(self) -> None:
        if self.session is None:
            headers = {"User-Agent": f"booksanon {self.email}"}
            self.session = aiohttp.ClientSession(headers=headers)

    async def close_session(self) -> None:
        if self.session:
            await self.session.close()
            self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.session.close()

    async def fetch_results(self, url):
        """Fetch results from the given URL with retry logic."""
        print(f"making request to {url}")
        for attempt in range(1, self.max_retries + 1):
            try:
                async with self.semaphore:
                    response = await self.session.get(url, timeout=10)
                    if response.status == 200:
                        return await response.json()
                    print(f"Attempt {attempt}: Received status {response.status}")
            except aiohttp.ClientError as e:
                print(f"Attempt {attempt}: Error - {e}")

            if attempt < self.max_retries:
                await asyncio.sleep(self.retry_delay)

        print("Failed to fetch data after retries.")
        return None
