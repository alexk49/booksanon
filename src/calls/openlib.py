"""
Module for creating URLs and parsing response from OpenLib API

https://openlibrary.org/dev/docs/api/books
"""
ROOT_URL = "https://openlibrary.org/search.json"


def get_general_query_url(search_query, limit: None | str=None) -> str:
    """
    Limit has to be a digit but should be passed as str
    """
    if limit and type(limit) is int:
        url = f"{ROOT_URL}?q={search_query}&limit={limit}"
    else:
        url = f"{ROOT_URL}?q={search_query}"
    print(f"created search url as {url}")
    return url

def get_complex_query_url(**kwargs) -> str:
    """
    Used for searches with specific parameters

    allowed_parms checks valid queries for open api lib

    >>> get_complex_query_url(title="Oliver Twist", author="Charles Dickens")
    >>> "https://openlibrary.org/search.json?title=Oliver Twist&author=Charles Dickens&limit=20"
    """
    allowed_params = ["title", "author", "limit"]

    url = f"{ROOT_URL}?"
    
    for key, value in kwargs.items():
        if key not in allowed_params:
            raise ValueError(f"Invalid parameter: {key}")

        if value:
            url += f"{key}={value}&"
    
    # Remove trailing "&" if it exists
    url = url.rstrip("&")

    print(f"Search URL created as: {url}")
    return url
