import sys

from calls.client import Client
from calls.google_books import GoogleBooksCaller
from calls.openlib import OpenLibCaller


def define_call_args(call_parser):
    call_parser.add_argument(
        "--api",
        type=str,
        choices=["openlibrary", "ol", "googlebooks", "gb"],
        default="openlibrary",
        help="Specify the API to use for the search (openlibrary or googlebooks)",
    )

    call_parser.add_argument(
        "-t",
        "--title",
        type=str,
        help="Book title for search",
    )
    call_parser.add_argument(
        "-a",
        "--author",
        type=str,
        help="Book author for search",
    )
    call_parser.add_argument(
        "-i",
        "--isbn",
        type=str,
        help="Book search for isbn",
    )
    call_parser.add_argument(
        "-l",
        "--limit",
        default=5,
        type=int,
        help="Limit number of results that come back",
    )
    call_parser.add_argument(
        "-c",
        "--complete",
        action="store_true",
        help="If passed then the full book data will be returned for search results",
    )
    # mutual exclusive args, generally for single purpose
    group = call_parser.add_mutually_exclusive_group()

    group.add_argument(
        "-editions",
        "--editions",
        type=str,
        help="Pass openlib work id and return filtered response from editions API.",
    )
    group.add_argument(
        "-auth-only",
        "--author-only",
        type=str,
        help="Pass openlib author id and return filtered response from editions API.",
    )
    group.add_argument(
        "-s",
        "--search",
        type=str,
        help="Search query for book results.",
    )
    group.add_argument(
        "-olwi",
        "--open-lib-work-id",
        type=str,
        help="Pass openlib work id and return response.",
    )
    return call_parser


async def call_open_lib(args, email_address):
    client = Client(email=email_address)
    caller = OpenLibCaller(client=client)

    if args.open_lib_work_id is not None:
        await caller.get_work_id_results(args.open_lib_work_id)
        await client.close_session()
        sys.exit()

    if args.author_only is not None:
        await caller.get_author_results(args.author_only)
        await client.close_session()
        sys.exit()

    if args.editions is not None:
        await caller.get_editions_only(args.editions)
        await client.close_session()
        sys.exit()

    if args.search:
        results = await caller.search_books(search_query=args.search, limit=args.limit)

    if args.title or args.author:
        await caller.search_books(title=args.title, author=args.author, limit=args.limit)

    if args.complete:
        complete_books, complete_authors = await caller.get_complete_books_data(results)

    await client.close_session()


async def call_google_books(args):
    client = Client()
    caller = GoogleBooksCaller(client=client)

    await caller.search_books(
        search_query=args.search,
        title=args.title,
        author=args.author,
        isbn=args.isbn,
        limit=args.limit,
    )

    await client.close_session()
