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
      example, complete parsed response:
    [{'name': 'Shirley Jackson',
      'death_date': '8 Aug 1965',
      'birth_date': '14 Dec 1916',
      'key': '/authors/OL507165A',
      'remote_ids': {'wikidata': 'Q239910',
                     'isni': '0000000121435300',
                     'viaf': '91864979'}},
    """
    name: str
    author_openlib_id: str  # "/authors/OL34184A"
    birth_date: int
    death_date: int
    remote_ids: dict


@dataclass
class Book:
    """
    Example complete parsed response:

    [{'title': 'We Have Always Lived in the Castle',
      'author_names': ['Shirley Jackson', 'Bernadette Dunne'],
      'author_keys': ['OL507165A', 'OL2865699A'],
      'first_publish_year': 1962,
      'openlib_work_key': '/works/OL3171087W',
      'cover_id': [11545332],
      'description': {'type': '/type/text',
                      'value': "Shirley Jackson's beloved gothic tale of a "
                               "peculiar girl named Merricat and her family's dark "
                               'secret\r\n'
                               '\r\n'
                               'Taking readers deep into a labyrinth of dark '
                               'neurosis, We Have Always Lived in the Castle is a '
                               'deliciously unsettling novel about a perverse, '
                               'isolated, and possibly murderous family and the '
                               'struggle that ensues when a cousin arrives at '
                               'their estate. This edition features a new '
                               'introduction by Jonathan Lethem.\r\n'
                               '\r\n'
                               'For more than seventy years, Penguin has been the '
                               'leading publisher of classic literature in the '
                               'English-speaking world. With more than 1,700 '
                               'titles, Penguin Classics represents a global '
                               'bookshelf of the best works throughout history and '
                               'across genres and disciplines. Readers trust the '
                               'series to provide authoritative texts enhanced by '
                               'introductions and notes by distinguished scholars '
                               'and contemporary authors, as well as up-to-date '
                               'translations by award-winning translators.'},
      'covers': [11545332,
                 8404336,
                 8903974,
                 8996442,
                 10203271,
                 10665482,
                 8774035,
                 13162383,
                 979990],
      'number_of_pages_median': 0,
      'isbns_13': {'9780140071078',
                   '9780141191454',
                   '9780141193939',
                   '9780141194998',
                   '9780141927558',
                   '9780143039976',
                   '9780143129547',
                   '9780143134831',
                   '9780445083219',
                   '9780670002900',
                   '9780670753437',
                   '9780881036916',
                   '9780891906230',
                   '9780899685328',
                   '9781441734266',
                   '9781441734280',
                   '9781441734297',
                   '9781441734327',
                   '9781445836324',
                   '9781445836331',
                   '9781789503869',
                   '9782266091015',
                   '9783257219258',
                   '9783865527097',
                   '9788845923661'},
      'isbns_10': {'0140071075',
                   '014119393X',
                   '0141194995',
                   '0143039970',
                   '0143129546',
                   '0143134833',
                   '0445083212',
                   '0670002909',
                   '0881036919',
                   '0891906231',
                   '0899685323',
                   '0948164360',
                   '1441734260',
                   '1441734287',
                   '1441734295',
                   '1441734325',
                   '1445836327',
                   '1445836335',
                   '1789503868',
                   '2266091018',
                   '3257219253',
                   '3865527094',
                   '8845923665'},
      'known_publishers': {'Adelphi',
                           'Amereon Ltd',
                           'Arcturus Publishing',
                           'Blackstone Audio, Inc.',
                           'Blackstone Audiobooks',
                           'Blackstone Pub',
                           'Chivers',
                           'Diogenes Verlag',
                           'Festa Verlag',
                           'Four Square',
                           'Lightyear Press',
                           'M. Joseph',
                           'Michael Joseph',
                           'PENGUIN BOOKS',
                           'Peguin Group',
                           'Penguin (Non-Classics)',
                           'Penguin Books',
                           'Penguin Books, Limited',
                           'Penguin Classics',
                           'Penguin Group UK',
                           'Penguin Publishing Group',
                           'Pocket',
                           'Popular Library',
                           'Quality Paperback Book Club',
                           'Robinson',
                           'Tandem Library',
                           'The Viking Press',
                           'Viking Press'}}]
    """

    title: str
    author_name: list[str]
    author_key: list[str]
    authors: list[Author]
    description: dict[str, str]
    first_publish_year: int
    openlib_work_key: str  # "key": "OL27448W",
    known_publishers: Set[str]
    isbns_13: Set[str]
    isbns_10: Set[str]
    openlib_cover_ids: Set[str]
    number_of_pages_median: int
