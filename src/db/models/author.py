from dataclasses import asdict, dataclass, field
from typing import Optional

from asyncpg import Record

from .utils import map_types_for_db


@dataclass
class Author:
    name: str
    remote_ids: dict[str, str] = field(default_factory=dict)
    id: Optional[int] = None  # only exists reading from db
    openlib_id: Optional[str] = None  # "/authors/OL34184A"
    birth_date: Optional[str] = None
    death_date: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    @classmethod
    def from_dict(cls, author_dict: dict) -> "Author":
        return cls(
            name=author_dict["name"],
            death_date=author_dict.get("death_date", None),
            birth_date=author_dict.get("birth_date", None),
            openlib_id=author_dict["key"],
            remote_ids=author_dict.get("remote_ids", {}),
        )

    def to_db_dict(self) -> dict:
        db_dict = asdict(self)
        return map_types_for_db(db_dict)

    @classmethod
    def from_db_record(cls, record: Record) -> "Author":
        return cls(
            id=record.get("id"),
            name=record.get("name"),
            remote_ids=record.get("remote_ids") or {},
            openlib_id=record.get("openlib_id"),
            birth_date=record.get("birth_date"),
            death_date=record.get("death_date"),
            created_at=record.get("created_at"),
            updated_at=record.get("created_at"),
        )
