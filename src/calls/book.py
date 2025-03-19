from dataclasses import dataclass
from typing import List, Set

# https://openlibrary.org/search/howto

# works url
# https://openlibrary.org/works/OL45804W.json
# editions url
# https://openlibrary.org/works/OL45804W/editions.json


@dataclass
class Author:
    name: str
    author_openlib_id: str  # "/authors/OL34184A"
    birth_date: int

@dataclass
class Book:
    title: str
    authors: List[Author]
    author: str
    subjects: Set[str]
    person: Set[str]
    first_publish_year: int
    openlib_work_key: str  # "key": "OL27448W", 
    publishers: Set[str]
    isbns: Set[str]
    openlib_cover_ids: Set[str]
    number_of_pages_median: int
