"""
Module for creating URLs and parsing response from OpenLib API

https://openlibrary.org/dev/docs/api/books
"""
ROOT_URL = "https://openlibrary.org"
SEARCH_URL = f"{ROOT_URL}/search.json"


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


def get_unique_work_keys(response: dict):
    work_keys = set()

    num_of_results = (len(response["docs"]))
    print(f"showing {num_of_results}")

    for num in range(num_of_results):
        work_key = response["docs"][num]["key"]
        print(f"work key found: {work_key}")
        work_keys.add(work_key)
    print(f"{len(work_keys)} unique works found from query")
    return work_keys


def get_work_id_url(work_id: str):
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
        return f"{ROOT_URL}{work_id}.json"
    elif work_id.startswith("OL"):
        work_id = f"/works/{work_id}"
        return f"{ROOT_URL}/{work_id}.json"
    else:
        print("invalid work id")
        return None
