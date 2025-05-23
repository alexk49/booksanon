from db import get_conn, load_queries


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
