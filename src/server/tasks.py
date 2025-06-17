from db.models import Book, Author
from . import resources


async def fetch_and_store_book_data(openlib_id: str, review: str, username="anon"):
    record = await resources.book_repo.get_book_by_openlib_id(openlib_id)

    if not record:
        book_data, complete_authors = await resources.openlib_caller.get_book_data_for_db(work_id=openlib_id)

        book = Book.from_dict(book_data)

        print("inserting book")
        book_id = await resources.book_repo.insert_book(book)

        for author_data in complete_authors:
            author = Author.from_dict(author_data)
            if not resources.book_repo.check_if_author_exists(author.openlib_id):
                print("inserting author")
                await resources.book_repo.insert_author(author)
    else:
        book = Book.from_db_record(record)
        book_id = book.id

    user_id = await resources.book_repo.get_user_id_by_username(username)

    print("inserting review")
    await resources.book_repo.insert_review(user_id["id"], book_id, review)
