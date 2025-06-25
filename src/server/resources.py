from calls.client import Client
from calls.openlib import OpenLibCaller
from db import DataBase
from repositories import BookRepository, QueueRepository
from . import settings


client = Client(email=settings.EMAIL_ADDRESS)
openlib_caller = OpenLibCaller(client=client)
db = DataBase(user=settings.POSTGRES_USERNAME, password=settings.POSTGRES_PASSWORD, url=settings.POSTGRES_URL)
book_repo = BookRepository(db=db)
queue_repo = QueueRepository(db=db)
