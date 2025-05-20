import pprint
from typing import Any, Dict, List, Optional, Set

from client import Client


class GoogleBooksCaller:
    def __init__(self, client: Client, pprint_results: bool = True):
        self.client = client
        self.pprint: bool = pprint_results
        self.base_url = "https://www.googleapis.com/books/v1/volumes"

    async def search_books(
        self, search_query=None, title=None, author=None, isbn=None, limit=5
    ):
        params = {
            "maxResults": limit,
            "printType": "books",
            "projection": "lite",
            "language": "en",
        }

        query_terms = []
        if search_query:
            query_terms.append(search_query)
        if title:
            query_terms.append(f"intitle:{title}")
        if author:
            query_terms.append(f"inauthor:{author}")
        if isbn:
            query_terms.append(f"isbn:{isbn}")

        if not query_terms:
            print(
                "Please provide a search query, title, author, or ISBN for Google Books."
            )
            return []

        params["q"] = "+".join(query_terms)
        search_url = self.base_url

        response = await self.client.fetch_results(search_url, params=params)

        results = response.get("items", [])
        print("Google Books Search Results:")

        for i, item in enumerate(results):
            volume_info = item.get("volumeInfo", {})
            print(f"\n--- Result {i + 1} ---")
            print(f"Title: {volume_info.get('title')}")
            authors = volume_info.get("authors", [])
            if authors:
                print(f"Author(s): {', '.join(authors)}")
            print(
                f"First Publish Year: {
                    volume_info.get('publishedDate', '').split('-')[0]
                }"
            )
            industry_identifiers = volume_info.get("industryIdentifiers", [])
            isbns = [
                id_data["identifier"]
                for id_data in industry_identifiers
                if id_data.get("type") in ["ISBN_10", "ISBN_13"]
            ]
            if isbns:
                print(f"ISBN(s): {', '.join(isbns)}")
            image_links = volume_info.get("imageLinks", {})
            print(f"Cover Link: {image_links.get('thumbnail')}")
            print(f"API ID: {item.get('id')}")

        pprint.pp(results)
        return results
