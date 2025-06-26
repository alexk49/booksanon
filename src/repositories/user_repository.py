from db import Database


class UserRepository:
    def __init__(self, db: Database):
        self.db = db

    """ Insert values """

    async def create_anon(self):
        """
        Used as default user
        """
        await self.db.run_query("create_anon")

    """ Get values """

    async def get_user_id_by_username(self, username: str) -> int | None:
        result = await self.db.run_query("get_user_id_by_username", username=username)
        return result["id"]
