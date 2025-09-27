import logging
from calls.client import Client
from calls.openlib import OpenLibCaller
from db import Database
from repositories import AuthorRepository, BookRepository, QueueRepository, ReviewRepository, UserRepository
from config import settings


logger = logging.getLogger("app")


class AppResourceContainer:
    def __init__(self):
        self.client = Client(email=settings.EMAIL_ADDRESS)
        self.openlib_caller = OpenLibCaller(client=self.client)
        self.db = Database(
            user=settings.POSTGRES_USER, password=settings.POSTGRES_PASSWORD, url=settings.POSTGRES_URL
        )

        self.review_repo = ReviewRepository(db=self.db)
        self.author_repo = AuthorRepository(db=self.db)
        self.book_repo = BookRepository(db=self.db, review_repo=self.review_repo)
        self.queue_repo = QueueRepository(db=self.db)
        self.user_repo = UserRepository(db=self.db)

    async def startup(self):
        await self.db.start_up()
        await self.user_repo.create_anon()
        logger.info("application resources started")

    async def shutdown(self):
        await self.db.close_down()
        await self.client.close_session()
        logger.info("application resources shutdown")


resources = AppResourceContainer()
