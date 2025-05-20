from dataclasses import dataclass
from typing import List, Set

# https://openlibrary.org/search/howto

# works url
# https://openlibrary.org/works/OL45804W.json
# editions url
# https://openlibrary.org/works/OL45804W/editions.json


@dataclass
class Author:
    """
      example, response:
          [{'name': 'Mervyn Peake',
    'death_date': '1968',
    'birth_date': '1911',
    'key': '/authors/OL2644841A',
    'bio': None,
    'remote_ids': {'viaf': '24606270',
                   'wikidata': 'Q6515',
                   'isni': '000000008365072X'}}]
    """

    name: str
    author_openlib_id: str  # "/authors/OL34184A"
    birth_date: int
    death_date: int
    bio: str
    remote_ids: dict


@dataclass
class Book:
    """
    Example response:

    [{'title': 'Titus Groan',
      'author_name': ['Mervyn Peake'],
      'author_key': ['OL2644841A'],
      'first_publish_year': 1946,
      'openlib_work_key': '/works/OL10473260W',
      'cover_id': [11730146],
      'authors': [{'type': {'key': '/type/author_role'},
                   'author': {'key': '/authors/OL2644841A'}}],
      'description': {'type': '/type/text',
                      'value': 'This is the first of the Gormenghast trilogy and '
                               'introduces the reader to Gormenghast Castle and '
                               'its inhabitants. Lord Sepulchrave the Earl of '
                               'Groan, his life an endless succession of '
                               'meaningless rituals, Countess Gertrude, who spends '
                               'her days secluded in her bedroom surrounded by '
                               'cats and birds, her only source of pleasure. Their '
                               'daughter Fuschia is there too, along with '
                               'Sepulchrave’s eccentric twin sisters, Cora and '
                               'Clarice and Mr. Flay, who leads Lord Sepulchrave '
                               'through the interminable rituals of the castle. '
                               'Into this world are thrust Titus, heir to the '
                               'Earldom and Steerpike, a Machiavellian kitchen boy '
                               'on the make.'},
      'covers': [11730146],
      'number_of_pages_median': 0,
      'known_isbns': {'0140060138', '0879511435', '0140027629', '0749300515'},
      'known_publishers': {'Ballantine Books',
                           'Book Club Assoc',
                           'Eyre & Spottiswoode',
                           'Eyre and Spottiswood',
                           'Harry N. Abrams',
                           'Mandarin',
                           'Overlook Press',
                           'Overlook Press / Methuen',
                           'Penguin',
                           'Penguin in association with Eyre & Spottiswoode',
                           'The Overlook Press'}}]
    """

    title: str
    author_name: list[str]
    author_key: list[str]
    authors: list[Author]
    description: dict[str, str]
    first_publish_year: int
    openlib_work_key: str  # "key": "OL27448W",
    known_publishers: Set[str]
    known_isbns: Set[str]
    openlib_cover_ids: Set[str]
    number_of_pages_median: int
