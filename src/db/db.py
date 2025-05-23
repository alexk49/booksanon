from pathlib import Path
import aiosql
import asyncpg

async def get_conn(user: str, password: str, url: str):
    if not user or not password or not url:
        print("unable to connect, invalid credentials")
        return None

    print(user)
    print(password)
    print(url) 
    return await asyncpg.connect(f"postgresql://{user}:{password}@{url}")


async def load_queries():
    dir_path = Path(__file__).parent
    queries = aiosql.from_path(dir_path / "sql", driver_adapter="asyncpg")
    return queries
