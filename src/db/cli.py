import os
import pprint
from pathlib import Path
import aiosql
import asyncpg

from calls.client import Client
from calls.openlib import OpenLibCaller
from db import DataBase
from db.models import Book, Author


def define_db_args(db_parser):
    db_parser.add_argument(
        "-cs",
        "--create-schema",
        action="store_true",
        help="Create db schema",
    )
    db_parser.add_argument(
        "-a",
        "--add-book",
        type=str,
        help="Pass Openlib work ID as str, to have book added to database.",
    )
    return db_parser


async def handle_db_args(args):
    POSTGRES_USERNAME = os.environ.get("POSTGRES_USERNAME")
    POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
    POSTGRES_URL = os.environ.get("POSTGRES_URL")

    async with DataBase(user=POSTGRES_USERNAME, password=POSTGRES_PASSWORD, url=POSTGRES_URL) as db:
        if args.create_schema:
            await db.create_schema()

        if args.add_book:
            client = Client(email=os.environ.get("EMAIL_ADDRESS"))
            caller = OpenLibCaller(client=client)

            book_data, complete_authors = await caller.get_book_data_for_db(work_id=args.add_book)

            book = Book.from_dict(book_data)

            pprint.pp(book)

            print("inserting book")
            await db.insert_book(book)

            for author_data in complete_authors:
                author = Author.from_dict(author_data)

                pprint.pp(author)

                print("inserting author")
                await db.insert_author(author)


async def create_schema(user, password, url):
    conn = await get_conn(user, password, url)
    queries = await load_queries()
    await queries.create_schema(conn)
    await conn.close()


async def get_conn(user: str, password: str, url: str):
    if not user or not password or not url:
        print("unable to connect, invalid credentials")
        return None

    return await asyncpg.connect(f"postgresql://{user}:{password}@{url}")


async def load_queries():
    dir_path = Path(__file__).parent
    queries = aiosql.from_path(dir_path / "sql", driver_adapter="asyncpg")
    return queries
