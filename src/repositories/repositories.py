from db import DataBase
from db.models import Author, Book


async def get_most_recent_books(db: DataBase, limit: int = 20) -> list[Book]:
    records = await db.run_query("get_most_recent_books", limit=limit)
    return Book.from_db_records(records)


async def create_schema(db: DataBase):
    print("setting up db schema")
    await db.run_query("create_schema")


async def insert_book(db: DataBase, book: Book):
    print("checking if book exists")
    existing_book = await db.run_query("get_book_by_openlib_work_key", openlib_work_key=book.openlib_work_key)

    if existing_book:
        print("book already exists")
        return
    return await db.run_query("insert_book", **book.to_db_dict())


async def insert_author(db: DataBase, author: Author):
    print("checking if author exists")
    existing_author = await db.run_query("get_author_by_openlib_id", openlib_id=author.openlib_id)

    if existing_author:
        print("author already exists")
        return
    return await db.run_query("insert_author", **author.to_db_dict())
