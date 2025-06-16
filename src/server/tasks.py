from db.models import Book, Author
from . import resources


async def fetch_and_store_book_data(openlib_id: str, review: str):
    print("fetching openlib data")
    book_data, complete_authors = await resources.openlib_caller.get_book_data_for_db(work_id=openlib_id)

    book = Book.from_dict(book_data)

    print("inserting book")
    await resources.book_repo.insert_book(book)

    for author_data in complete_authors:
        author = Author.from_dict(author_data)
        print("inserting author")
        await resources.book_repo.insert_author(author)
