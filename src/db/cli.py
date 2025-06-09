import os
import pprint

from repositories import BookRepository
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
        book_repo = BookRepository(db=db)

        if args.create_schema:
            await db.create_schema()

        if args.add_book:
            client = Client(email=os.environ.get("EMAIL_ADDRESS"))
            caller = OpenLibCaller(client=client)

            book_data, complete_authors = await caller.get_book_data_for_db(work_id=args.add_book)

            book = Book.from_dict(book_data)

            pprint.pp(book)

            print("inserting book")
            await book_repo.insert_book(db, book)

            for author_data in complete_authors:
                author = Author.from_dict(author_data)

                pprint.pp(author)

                print("inserting author")
                await book_repo.insert_author(db, author)
