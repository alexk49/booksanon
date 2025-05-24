"""
Class for making calls to OpenLib API

https://openlibrary.org/dev/docs/api/books

API response comes in dict but actual,
book data is nested in list under docs

This means you can loop through the actual books results with:

>>> num_of_results = (len(response["docs"]))
>>> for num in range(num_of_results):
>>>    book = response["docs"][num]

Cover Ids can be read into URLs with:
>>> cover_id = book["cover_i"]
>>> cover_id_img = f"https://covers.openlibrary.org/b/id/{cover_id}-S.jpg"
"""

import pprint
from typing import Any, Dict, List, Optional, Set

from calls.client import Client


class OpenLibCaller:
    def __init__(self, client: Client, pprint_results: bool = True):
        self.client = client
        self.pprint: bool = pprint_results
        self.root_url = "https://openlibrary.org"
        self.search_url = f"{self.root_url}/search.json"

    """ Calls to API """

    async def get_work_id_results(self, work_id: str):
        """Fetch and optionally parse work ID results"""
        url = self.get_work_id_url(work_id)
        response = await self.client.fetch_results(url)

        book = OpenLibCaller.parse_work_id_page(response)

        if self.pprint:
            pprint.pp(book)
        return book

    async def get_editions_only(self, work_id: str):
        url = self.get_editions_url(work_id)
        response = await self.client.fetch_results(url)

        if self.pprint:
            pprint.pp(response)

        return response

    async def get_author_results(self, author_id: str):
        url = self.get_author_url(author_id)
        response = await self.client.fetch_results(url)

        author = self.parse_author_id_page(response)

        if self.pprint:
            pprint.pp(author)
        return author

    async def search_books(
        self,
        title: Optional[str] = None,
        author: Optional[str] = None,
        search_query: Optional[str] = None,
        limit: int = 10,
        lang: str = "en",
    ) -> List[Dict[str, Any]]:
        """
        Limit is used as str in search URLs, but is used as int to index on parsers.

        Makes sense to keep it as int when passed to make sure it is a digit.
        """

        if title or author:
            url = self.get_complex_query_url(
                title=title,
                author=author,
                limit=str(limit),
                lang=lang,
            )
        elif search_query:
            url = self.get_general_query_url(search_query, limit=str(limit), lang=lang)
        else:
            raise ValueError("Must provide either title/author or general search_query")

        results = await self.client.fetch_results(url)

        clean_results = OpenLibCaller.parse_books_search_results(results, limit)

        if self.pprint:
            pprint.pp(clean_results)
        return clean_results

    async def get_complete_books_data(self, clean_results: list[dict]):
        complete_books = []
        complete_authors = []

        for book in clean_results:
            complete_book = await self._get_complete_book_data(book)
            complete_books.append(complete_book)

        authors_response_keys = []

        for book in complete_books:
            authors_key_list: list = book["author_keys"]

            for author_key in authors_key_list:
                authors_response_keys.append(author_key)

        for author_key in authors_response_keys:
            author = await self.get_author_results(author_key)
            complete_authors.append(author)

        if self.pprint:
            pprint.pp(complete_books)

        if self.pprint:
            pprint.pp(complete_authors)
        return complete_books, complete_authors

    async def _get_complete_book_data(self, book: dict) -> dict:
        """Internal method to get complete book data"""
        work_id = book["openlib_work_key"]

        work_url = self.get_work_id_url(work_id)
        work_response = await self.client.fetch_results(work_url)

        book = OpenLibCaller.parse_work_id_page(work_response, book=book)

        editions_url = self.get_editions_url(work_id)
        editions_response = await self.client.fetch_results(editions_url)

        book = OpenLibCaller.parse_editions_response(response=editions_response, book=book)

        return book

    """ Methods for constructing URLs """

    def get_general_query_url(self, search_query: str, limit: str = "1", lang: str = "en") -> str:
        """
        Limit has to be a digit but should be passed as str,
        this does not limit actual results but limits pages of results so default is 1
        """
        if limit and type(limit) is int:
            url = f"{self.search_url}?q={search_query}&limit={limit}&lang={lang}"
        else:
            url = f"{self.search_url}?q={search_query}"
        print(f"created search url as {url}")
        return url

    def get_complex_query_url(self, **kwargs) -> str:
        """
        Used for searches with specific parameters

        allowed_parms checks valid queries for open api lib
        https://openlibrary.org/search/howto

        >>> get_complex_query_url(title="Oliver Twist", author="Charles Dickens")
        >>> "https://openlibrary.org/search.json?title=Oliver Twist&author=Charles Dickens&limit=20"
        """
        allowed_params = [
            "title",
            "author",
            "subject",
            "publisher",
            "publish_year",
            "limit",
            "lang",
        ]

        url = f"{self.search_url}?"

        for key, value in kwargs.items():
            if key not in allowed_params:
                raise ValueError(f"Invalid parameter: {key}")

            if value:
                url += f"{key}={value}&"

        # Remove trailing "&" if it exists
        url = url.rstrip("&")

        print(f"Search URL created as: {url}")
        return url

    def get_author_url(self, author_id: str):
        """
        Author IDs will look like OL1A, or OL2644841A.

        Then these can be used for the author pages like:
        http://openlibrary.org/authors/OL1A.json
        """
        if author_id.startswith("/authors/"):
            return f"{self.root_url}{author_id}.json"
        elif author_id.startswith("OL"):
            author_id = f"/authors/{author_id}"
            return f"{self.root_url}{author_id}.json"
        else:
            print("invalid author id passed")
            return None

    def get_work_id_url(self, work_id: str):
        """
        Work ids should look like below,
        as this is taken straight from ol api:
        /works/OL24214484W

        But will accept:
        OL24214484W

        This allows construction of the work_id url, like:
        https://openlibrary.org/works/OL45804W.json
        """
        if work_id.startswith("/works/"):
            return f"{self.root_url}{work_id}.json"
        elif work_id.startswith("OL"):
            work_id = f"/works/{work_id}"
            return f"{self.root_url}{work_id}.json"
        else:
            print("invalid work id")
            return None

    def get_editions_url(self, work_id):
        return self.get_work_id_url(work_id).replace(".json", "/editions.json")

    """ Methods for parsing api responses """

    @staticmethod
    def parse_editions_response(response: Dict[str, Any], book: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Parse book information from a response, extracting unique ISBNs and publishers.

        Args:
            response: A dictionary containing book entries
            book: Optional existing book dictionary to update

        Returns:
            Updated book dictionary with known ISBNs and publishers
        """
        book = book or {}

        isbns_13: Set[str] = set()
        isbns_10: Set[str] = set()
        known_publishers: Set[str] = set()

        for entry in response.get("entries", []):
            isbns_13.update(entry.get("isbn_13", []))
            isbns_10.update(entry.get("isbn_10", []))

            known_publishers.update(entry.get("publishers", []))

        book.update({"isbns_13": isbns_13, "isbns_10": isbns_10, "known_publishers": known_publishers})
        return book

    @staticmethod
    def count_num_of_books_in_response(response: dict):
        num_of_results = len(response["docs"])
        print(f"showing {num_of_results}")
        return num_of_results

    @staticmethod
    def parse_books_search_results(response: dict, limit: int | None = None) -> List[Dict[str, Any]]:
        books: list = []

        if limit:
            num_of_results: int = len(response["docs"][0:limit])
        else:
            num_of_results = len(response["docs"])

        for num in range(num_of_results):
            book: dict = response["docs"][num]
            books.append(
                {
                    "title": book.get("title", "Unknown"),
                    "author_names": book.get("author_name", []),
                    "author_keys": book.get("author_key", []),
                    "first_publish_year": book.get("first_publish_year", "Unknown"),
                    "openlib_work_key": book.get("key", "Unknown"),
                    "cover_id": [book.get("cover_i")],
                }
            )

        return books

    @staticmethod
    def parse_author_id_page(response: Dict[str, Any], author: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if author is None:
            author = {}

        author.update(
            {
                "name": response.get("name", ""),
                "death_date": response.get("death_date", ""),
                "birth_date": response.get("birth_date", ""),
                "key": response.get("key", ""),
                "remote_ids": response.get("remote_ids", {}),
            }
        )

        return author

    @staticmethod
    def parse_work_id_page(response: Dict[str, Any], book: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        This is used to parse the work id urls, to get complete metadata for each book.

        e.g:
        https://openlibrary.org//works/OL82563W.json

        If a dictionary is provided as `book`, it updates that dictionary. Expected use case is to pass,
        dictionary of inital search results from self.search_url.

        If no dict is passed then it creates and returns a new dictionary.

        Args:
            response (dict): The API response containing book data.
            book (dict, optional): An existing dictionary to update. Defaults to None.

        Returns:
            dict: A dictionary containing the parsed book metadata.

        On its own it won't return the below

         # got from editions
         'publishers': [],
         'isbns': [],
         # got from search url page
         first_year_publish

         author_name and author_key is returned on the book search search results, but authors returns on works
        """
        if book is None:
            book = {}

        book.update(
            {
                "title": response.get("title", ""),
                # "authors": response.get("authors", []),
                "description": response.get("description", {}),
                "openlib_work_key": response.get("key", "Unknown"),
                "covers": response.get("covers", []),
                "number_of_pages_median": response.get("number_of_pages_median", 0),
            }
        )

        return book
