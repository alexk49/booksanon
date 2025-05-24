from pathlib import Path
import aiosql
import asyncpg


def define_db_args(db_parser):
    db_parser.add_argument(
        "-cs",
        "--create-schema",
        action="store_true",
        help="Create db schema",
    )
    return db_parser


async def create_schema(user, password, url):
    conn = await get_conn(user, password, url)
    queries = await load_queries()
    await queries.create_schema(conn)
    await conn.close()


async def get_conn(user: str, password: str, url: str):
    if not user or not password or not url:
        print("unable to connect, invalid credentials")
        return None

    return await asyncpg.connect(f"postgresql://{user}:{password}@{url}")


async def load_queries():
    dir_path = Path(__file__).parent
    queries = aiosql.from_path(dir_path / "sql", driver_adapter="asyncpg")
    return queries
