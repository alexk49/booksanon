import asyncio

from calls.client import Client
from calls.openlib import OpenLibCaller
from db import Database
from repositories import QueueRepository, AuthorRepository, BookRepository, ReviewRepository, UserRepository
from . import settings


class HueyResourceContainer:
    def __init__(self):
        self.db = Database(
            user=settings.POSTGRES_USERNAME, password=settings.POSTGRES_PASSWORD, url=settings.POSTGRES_URL
        )

        self.client = Client(email=settings.EMAIL_ADDRESS)
        self.openlib_caller = OpenLibCaller(client=self.client, max_concurrent_requests=1)

        self.queue_repo = QueueRepository(db=self.db)
        self.author_repo = AuthorRepository(db=self.db)
        self.review_repo = ReviewRepository(db=self.db)
        self.book_repo = BookRepository(db=self.db, review_repo=self.review_repo)
        self.user_repo = UserRepository(db=self.db)

        self.loop: asyncio.AbstractEventLoop | None = None

    async def _async_startup(self):
        await self.db.start_up()
        print("huey resources database pool started")

    async def _async_shutdown(self):
        await self.client.close_session()
        print("closing down huey resources")

    def startup(self):
        if self.loop is None:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.loop.run_until_complete(self._async_startup())

    def shutdown(self):
        if self.loop and self.loop.is_running():
            self.loop.run_until_complete(self._async_shutdown())
            self.loop.close()
            asyncio.set_event_loop(None)
            print("shutting down huey resources event loop")


resources = HueyResourceContainer()
