import asyncio
from pathlib import Path

from calls.client import Client
from calls.openlib import OpenLibCaller
from db import DataBase
from db.models import Book, Author
from repositories import QueueRepository, BookRepository
from . import settings
from huey import SqliteHuey

huey_db = Path(settings.PROJECT_ROOT / "data" / "huey_queue.db")
huey = SqliteHuey("queue", filename=huey_db)


@huey.task()
def process_review_submission(submission_id):
    asyncio.run(_async_process_review_submission(submission_id))


async def _async_process_review_submission(submission_id):
    db = DataBase(user=settings.POSTGRES_USERNAME, password=settings.POSTGRES_PASSWORD, url=settings.POSTGRES_URL)
    await db.start_up()
    queue_repo = QueueRepository(db=db)

    submission = await queue_repo.read_form_submission(submission_id)

    if not submission:
        print(f"no submission found with id: {submission_id}")
        return

    openlib_id = submission["openlib_id"]
    review = submission["review"]

    result = await fetch_and_store_book_data(db, openlib_id, review)

    if not result:
        print(f"error adding in openlib_id: {openlib_id}, id: {submission_id}")

    await queue_repo.complete_form_submission(submission_id=submission_id)
    print(f"[Huey] Submission {submission_id} completed.")


async def fetch_and_store_book_data(db, openlib_id: str, review: str, username="anon") -> bool:
    client = Client(email=settings.EMAIL_ADDRESS)
    openlib_caller = OpenLibCaller(client=client, max_concurrent_requests=1)

    book_repo = BookRepository(db=db)

    print(f"fetching book data for {openlib_id}")
    record = await book_repo.get_book_by_openlib_id(openlib_id)

    if not record:
        book_data, complete_authors = await openlib_caller.get_book_data_for_db(work_id=openlib_id)

        book = Book.from_dict(book_data)

        print(f"inserting book: {book}")
        book_id = await book_repo.insert_book(book)

        for author_data in complete_authors:
            author = Author.from_dict(author_data)
            author_id = await book_repo.get_author_id_by_openlib_id(author.openlib_id)

            if not author_id:
                print(f"inserting author: {author}")
                author_id = await book_repo.insert_author(author)

            print(f"linking book to author: book_id: {book_id}, author_id: {author_id}")
            await book_repo.link_book_author(book_id, author_id)
    else:
        book = Book.from_db_record(record)
        book_id = book.id

    user_id = await book_repo.get_user_id_by_username(username)

    print(f"got user_id: {user_id}")

    print(f"inserting review: {review}")
    await book_repo.insert_review(user_id["id"], book_id, review)
    return True
