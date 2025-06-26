from calls.client import Client
from calls.openlib import OpenLibCaller
from db import Database
from repositories import AuthorRepository, BookRepository, QueueRepository, ReviewRepository, UserRepository
from . import settings


client = Client(email=settings.EMAIL_ADDRESS)
openlib_caller = OpenLibCaller(client=client)
db = Database(user=settings.POSTGRES_USERNAME, password=settings.POSTGRES_PASSWORD, url=settings.POSTGRES_URL)
author_repo = AuthorRepository(db=db)
book_repo = BookRepository(db=db)
queue_repo = QueueRepository(db=db)
review_repo = ReviewRepository(db=db)
user_repo = UserRepository(db=db)
