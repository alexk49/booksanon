from db import DataBase


class QueueRepository:
    def __init__(self, db: DataBase):
        self.db = db

    async def insert_review_submission(self, openlib_id: str, review: str, username: str = "anon"):
        return await self.db.run_query(
            "insert_review_submission", openlib_id=openlib_id, review=review, username=username
        )

    async def read_form_submission(self, submission_id):
        return await self.db.run_query("read_form_submission", submission_id=submission_id)

    async def complete_form_submission(self, submission_id: int):
        return await self.db.run_query("complete_form_submission", submission_id=submission_id)
