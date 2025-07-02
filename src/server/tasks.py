from pathlib import Path

from huey import SqliteHuey

from db.models import Author, Book
from . import settings
from .huey_resources import resources


huey_db = Path(settings.PROJECT_ROOT / "data" / "huey_queue.db")
huey = SqliteHuey("queue", filename=huey_db)


@huey.on_startup()
def on_startup():
    resources.startup()


@huey.on_shutdown()
def on_shutdown():
    resources.shutdown()


@huey.task()
def process_review_submission(submission_id):
    if not resources.loop:
        print("no loop set for huey tasks. Cannot process task")

    resources.loop.run_until_complete(_async_process_review_submission(submission_id))


async def _async_process_review_submission(submission_id):
    submission = await resources.queue_repo.read_form_submission(submission_id)

    if not submission:
        print(f"no submission found with id: {submission_id}")
        return

    openlib_id = submission["openlib_id"]
    review = submission["review"]
    username = submission.get("username", "anon")

    try:
        result = await _fetch_and_store_book_data(openlib_id, review, username)

        if not result:
            print(f"error adding in openlib_id: {openlib_id}, id: {submission_id}")

        await resources.queue_repo.complete_form_submission(submission_id=submission_id)
        print(f"[Huey] Submission {submission_id} completed.")
    except Exception as exc:
        print(f"there was an error processing submission id: {submission_id}: {exc}")


async def _fetch_and_store_book_data(openlib_id: str, review: str, username="anon") -> bool:
    print(f"fetching book data for {openlib_id}")
    book = await resources.book_repo.get_book_by_openlib_id(openlib_id)

    if not book:
        book_data, complete_authors = await resources.openlib_caller.get_book_data_for_db(work_id=openlib_id)

        book = Book.from_dict(book_data)

        print(f"inserting book: {book}")
        book_id = await resources.book_repo.insert_book(book)

        print(f"checking author data: {complete_authors}")

        for author_data in complete_authors:
            if not author_data:
                print("skipping empty author")
                continue

            author = Author.from_dict(author_data)
            print(author)
            print("checking if author exists in db")
            author_id = await resources.author_repo.get_author_id_by_openlib_id(author.openlib_id)

            if not author_id:
                print(f"inserting author: {author}")
                author_id = await resources.author_repo.insert_author(author)

            print(f"linking book to author: book_id: {book_id}, author_id: {author_id}")
            await resources.book_repo.link_book_author(book_id, author_id)
    else:
        book_id = book.id

    user_id = await resources.user_repo.get_user_id_by_username(username)

    print(f"got user_id: {user_id}")

    print(f"inserting review: {review}")
    await resources.review_repo.insert_review(user_id, book_id, review)
    return True
