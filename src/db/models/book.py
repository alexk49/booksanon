import json
import logging
import random
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Optional, Union

from asyncpg import Record

from . import Author
from .utils import make_json_safe, map_types_for_db


logger = logging.getLogger("app")


@dataclass
class Book:
    title: str
    openlib_work_key: str
    author_names: list[str]
    author_keys: list[str]

    id: Optional[int] = None  # only used when reading from db
    authors: Optional[list[Author]] = None

    # Metadata
    first_publish_year: Optional[str] = None
    number_of_pages_median: Optional[int] = None
    openlib_description: Optional[str] = None
    openlib_tags: set[str] = field(default_factory=set)
    publishers: set[str] = field(default_factory=set)
    isbns_13: set[str] = field(default_factory=set)
    isbns_10: set[str] = field(default_factory=set)
    openlib_cover_ids: list[str] = field(default_factory=list)
    cover_id: Optional[str] = None

    remote_links: Optional[Union[list[dict[str, str]], str]] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_db_record(cls, record: Record) -> Optional["Book"]:
        if not record:
            return None

        cover_id = record.get("cover_id", "")
        openlib_cover_ids = record.get("openlib_cover_ids", [])
        return cls(
            id=record.get("book_id"),
            title=record.get("title", ""),
            authors=cls._parse_authors(record.get("authors")),
            author_names=record.get("author_names", []),
            author_keys=record.get("author_keys", []),
            openlib_work_key=record.get("openlib_work_key", ""),
            publishers=set(record.get("publishers", [])),
            isbns_13=set(record.get("isbns_13", [])),
            isbns_10=set(record.get("isbns_10", [])),
            cover_id = cover_id or cls._pick_cover_id(openlib_cover_ids),
            openlib_cover_ids=openlib_cover_ids,
            number_of_pages_median=record.get("number_of_pages_median"),
            openlib_description=record.get("openlib_description"),
            openlib_tags=set(record.get("openlib_tags", [])),
            remote_links=record.get("remote_links") or [],
            first_publish_year=record.get("first_publish_year"),
            created_at=record.get("created_at"),
            updated_at=record.get("updated_at"),
        )

    @classmethod
    def from_db_records(cls, records: list[Record]) -> list[Optional["Book"]]:
        """
        Converts an iterable of database records into a list of Book objects.
        """
        return [cls.from_db_record(r) for r in records]

    @classmethod
    def from_dict(cls, book_dict: dict) -> "Book":
        description = cls._parse_description(book_dict.get("description", None))
        cover_ids_from_api = book_dict.get("covers", [])

        return cls(
            title=book_dict["title"],
            author_names=book_dict["author_names"],
            author_keys=book_dict["author_keys"],
            first_publish_year=book_dict["first_publish_year"],
            openlib_work_key=book_dict["openlib_work_key"],
            cover_id=str(book_dict.get("cover_id", [])[0]),
            openlib_cover_ids=[str(cid) for cid in cover_ids_from_api],
            openlib_description=description,
            openlib_tags=set(book_dict.get("subjects", [])),
            remote_links=book_dict.get("links"),
            number_of_pages_median=book_dict.get("number_of_pages_median", 0),
            isbns_13=book_dict.get("isbns_13", []),
            isbns_10=book_dict.get("isbns_10", []),
            publishers=book_dict.get("publishers", []),
        )

    def to_db_dict(self) -> dict:
        db_dict = asdict(self)
        return map_types_for_db(db_dict)

    def to_json_dict(self) -> dict:
        return make_json_safe(self)

    """ Helper methods """

    @staticmethod
    def _parse_authors(raw_authors: Union[str, list[dict[str, Any]], None]) -> list[Author]:
        try:
            authors_dict = json.loads(raw_authors) if isinstance(raw_authors, str) else raw_authors
            return [Author(id=int(author["id"]), name=author["name"]) for author in authors_dict or []]
        except Exception as exc:
            logger.info(f"error reading authors: {raw_authors}, {exc}")
            return []

    @staticmethod
    def _parse_description(description_raw: Union[dict, str, None]) -> Optional[str]:
        if isinstance(description_raw, dict):
            return description_raw.get("value")
        elif isinstance(description_raw, str):
            return description_raw
        return None

    @staticmethod
    def _parse_remote_links(remote_links_raw: str) -> list[dict[str, str]]:
        try:
            return json.loads(remote_links_raw) if remote_links_raw else []
        except json.JSONDecodeError as exc:
            logger.info(f"Error parsing remote links: {exc}")
            return []

    @staticmethod
    def _pick_cover_id(cover_ids: list[str]) -> Optional[str]:
        return random.choice(cover_ids) if cover_ids else None

    """ Properties """

    @property
    def author_display(self) -> str:
        return ", ".join(self.author_names) if self.author_names else "Unknown"

    @property
    def tags_display(self) -> list[str]:
        if not self.openlib_tags:
            return []
        return sorted(self.openlib_tags)

    @property
    def publishers_display(self) -> list[str]:
        """
        Returns the set of publishers as a sorted list,
        ready for display and slicing in a template.
        """
        return sorted(self.publishers) if self.publishers else []

    @property
    def link_outs(self) -> list[dict[str, str | None]]:
        links = []

        if self.remote_links:
            if isinstance(self.remote_links, str):
                rl: list = self._parse_remote_links(self.remote_links)
            else:
                rl = self.remote_links

            links.extend(
                [
                    {"text": link.get("title"), "url": link.get("url")}
                    for link in rl
                    if link.get("title") and link.get("url")
                ]
            )

        if self.openlib_work_key:
            if self.openlib_work_key.startswith("/works/"):
                links.append({"text": "OpenLibrary", "url": f"https://openlibrary.org{self.openlib_work_key}"})
            else:
                links.append({"text": "OpenLibrary", "url": f"https://openlibrary.org/works/{self.openlib_work_key}"})

        if self.author_display and self.author_display != "Unknown":
            search_query = f"{self.title}+{self.author_display}".replace(" ", "+")
        else:
            search_query = f"{self.title}".replace(" ", "+")

        links.append({"text": "uk.bookshop.org", "url": f"https://uk.bookshop.org/search?keywords={search_query}"})
        links.append({"text": "us.bookshop.org", "url": f"https://bookshop.org/search?keywords={search_query}"})
        links.append({"text": "librofm", "url": f"https://libro.fm/search?utf8=%E2%9C%93&q={search_query}"})
        return links

    @property
    def filtered_link_outs(self) -> list[dict[str, str | None]]:
        allowed_texts = {"OpenLibrary", "uk.bookshop.org", "us.bookshop.org", "librofm"}
        return [link for link in self.link_outs if link["text"] in allowed_texts]
