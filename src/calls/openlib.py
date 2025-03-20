"""
Module for creating URLs and parsing response from OpenLib API

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
from typing import Any, Dict, List, Optional


ROOT_URL = "https://openlibrary.org"
SEARCH_URL = f"{ROOT_URL}/search.json"


""" Create URLs """

def get_general_query_url(search_query, limit: None | str=None) -> str:
    """
    Limit has to be a digit but should be passed as str
    """
    if limit and type(limit) is int:
        url = f"{SEARCH_URL}?q={search_query}&limit={limit}"
    else:
        url = f"{SEARCH_URL}?q={search_query}"
    print(f"created search url as {url}")
    return url

def get_complex_query_url(**kwargs) -> str:
    """
    Used for searches with specific parameters

    allowed_parms checks valid queries for open api lib
    https://openlibrary.org/search/howto

    >>> get_complex_query_url(title="Oliver Twist", author="Charles Dickens")
    >>> "https://openlibrary.org/search.json?title=Oliver Twist&author=Charles Dickens&limit=20"
    """
    allowed_params = ["title", "author", "subject", "publisher", "publish_year", "limit"]

    url = f"{SEARCH_URL}?"
    
    for key, value in kwargs.items():
        if key not in allowed_params:
            raise ValueError(f"Invalid parameter: {key}")

        if value:
            url += f"{key}={value}&"
    
    # Remove trailing "&" if it exists
    url = url.rstrip("&")

    print(f"Search URL created as: {url}")
    return url


def get_work_id_url(work_id: str, editions=False):
    """
    Work ids should look like below,
    as this is taken straight from ol api:
    /works/OL24214484W

    But will accept:
    OL24214484W

    This allows construction of the work_id url, like:
    https://openlibrary.org/works/OL45804W.json

    Editions switch can be used to get editions URL:
    https://openlibrary.org/works/OL45804W/editions.json
    """
    if work_id.startswith("/works/"):
        base_url = f"{ROOT_URL}{work_id}"
    elif work_id.startswith("OL"):
        work_id = f"/works/{work_id}"
        base_url = f"{ROOT_URL}/{work_id}"
    else:
        print("invalid work id")
        return None

    if editions:
        return f"{base_url}/editions.json"
    else:
        return f"{base_url}.json"


""" Parse response """

def get_num_of_books_in_response(response: dict):
    num_of_results = (len(response["docs"]))
    print(f"showing {num_of_results}")
    return num_of_results


def get_unique_work_keys(response: dict):
    work_keys = set()

    num_of_results = get_num_of_books_in_response(response) 

    for num in range(num_of_results):
        work_key = response["docs"][num]["key"]
        print(f"work key found: {work_key}")
        work_keys.add(work_key)
    print(f"{len(work_keys)} unique works found from query")
    return work_keys


def process_books_search_results(response: dict) -> List[Dict[str, Any]]:
    processed_books: list = []
    
    num_of_results: int = (len(response["docs"]))

    for num in range(num_of_results):
        book: dict = response["docs"][num]
        processed_books.append({
            "title": book.get("title", "Unknown"),
            "author_name": book.get("author_name", []),
            "author_key": book.get("author_key", []),
            "first_publish_year": book.get("first_publish_year", "Unknown"),
            "openlib_work_key": book.get("key", "Unknown"), 
            "cover_ids": [book.get("cover_i")],
        })

    return processed_books


def parse_workid_page(response: Dict[str, Any], book: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    This is used to parse the work id urls, to get complete metadata for each book.

    e.g:
    https://openlibrary.org//works/OL82563W.json

    If a dictionary is provided as `book`, it updates that dictionary. Expected use case is to pass,
    dictionary of inital search results from SEARCH_URL.

    If no dict is passed then it creates and returns a new dictionary.

    Args:
        response (dict): The API response containing book data.
        book (dict, optional): An existing dictionary to update. Defaults to None.

    Returns:
        dict: A dictionary containing the parsed book metadata.

    On its own it won't return:

     'publishers': [],
     'isbns': [],
     first_year_publish
    """
    if book is None:
        book = {}

    book.update({
        "title": response.get("title", ""),
        # "author": response.get("author_name", []),
        # "author_key": response.get("author_key", []),
        "authors": response.get("authors", []),
        # maybe shouldn't collect this:
        # "first_publish_year": response.get("first_publish_year", "Unknown"),
        # may need these from editions page:
        # "publishers": response.get("publisher", []),
        # "isbns": response.get("isbn", []),
        "description": response.get("description", {}),
        "openlib_work_key": response.get("key", "Unknown"),
        "covers": response.get("covers", []),
        "number_of_pages_median": response.get("number_of_pages_median", 0),
        "subjects": response.get("subjects", []),
        "subject_people": response.get("subject_people", []),
        "subject_places": response.get("subject_places", []),
        "excerpts": response.get("excerpts", []),
    })
    
    return book
