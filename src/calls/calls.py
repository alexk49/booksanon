import argparse
import os
import sys

import aiohttp
import asyncio
from dotenv import load_dotenv


load_dotenv()
EMAIL_ADDRESS = os.environ["EMAIL_ADDRESS"]


class APIClient:
    """
    Async api client for making requests
    """

    def __init__(self, max_concurrent_requests=3, max_retries=3, retry_delay=3, email_address=EMAIL_ADDRESS) -> None:
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.semaphore = asyncio.Semaphore(max_concurrent_requests)
        self.session = None

    async def create_session(self, email=EMAIL_ADDRESS):
        if self.session is None:
            headers = {"User-Agent": f"booksanon ({email})"}
            self.session = aiohttp.ClientSession(headers=headers)

    async def close_session(self):
        if self.session:
            await self.session.close()
            self.session = None

    async def fetch_results(self, url):
        """Fetch results from the given URL with retry logic."""
        print(f"making request to {url}")
        for attempt in range(1, self.max_retries + 1):
            try:
                async with self.semaphore:
                    async with self.session.get(url, timeout=10) as response:
                        if response.status == 200:
                            return await response.json()
                        print(f"Attempt {attempt}: Received status {response.status}")
            except aiohttp.ClientError as e:
                print(f"Attempt {attempt}: Error - {e}")

            if attempt < self.max_retries:
                await asyncio.sleep(self.retry_delay)

        print("Failed to fetch data after retries.")
        return None


class OpenLibCalls(APIClient):
    root_url = "https://openlibrary.org/search.json"

    def __init__(self):
        super().__init__()

    def get_general_query_url(self, search_query, limit: None | str = None) -> str:
        """
        Limit has to be a digit but should be passed as str
        """
        if limit and type(limit) is int:
            url = self.root_url + "?q=" + search_query + f"&limit={limit}"
        else:
            url = self.root_url + "?q=" + search_query
        print(f"created search url as {url}")
        return url

    def get_complex_query_url(self, **kwargs) -> str:
        """
        Used for searches with specific parameters

        allowed_parms checks valid queries for open api lib

        >>> get_complex_query_url(title="Oliver Twist", author="Charles Dickens")
        >>> "https://openlibrary.org/search.json?title=Oliver Twist&author=Charles Dickens&limit=20"
        """
        allowed_params = ["title", "author", "limit"]

        url = self.root_url + "?"

        for key, value in kwargs.items():
            if key not in allowed_params:
                raise ValueError(f"Invalid parameter: {key}")

            if value:
                url += f"{key}={value}&"

        # Remove trailing "&" if it exists
        url = url.rstrip("&")

        print(f"Search URL created as: {url}")
        return url


def set_arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-t",
        "--title",
        type=str,
        help="Book title for search",
    )
    parser.add_argument(
        "-a",
        "--author",
        type=str,
        help="Book author for search",
    )
    parser.add_argument(
        "-s",
        "--search",
        type=str,
        help="Search query for book results.",
    )
    return parser


async def main():
    parser = set_arg_parser()

    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    search_query = args.search
    title = args.title
    author = args.author

    client = OpenLibCalls()

    if search_query:
        search_url = client.get_general_query_url(search_query, limit="20")
    else:
        search_url = client.get_complex_query_url(title=title, author=author, limit="20")

    await client.create_session()

    results = await client.fetch_results(search_url)

    print("results:")
    print(results)

    await client.close_session()


asyncio.run(main())
