#!/usr/bin/env python3
import asyncio
import argparse
import os
import sys

from dotenv import load_dotenv

from client import Client
from openlib import OpenLibCaller


load_dotenv()
EMAIL_ADDRESS = os.environ["EMAIL_ADDRESS"]


def set_arg_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-t",
        "--title",
        type=str,
        help="Book title for search",
    )
    parser.add_argument(
        "-a",
        "--author",
        type=str,
        help="Book author for search",
    )
    parser.add_argument(
        "-l",
        "--limit",
        default=5,
        type=int,
        help="Limit number of results that come back",
    )
    parser.add_argument(
        "-c",
        "--complete",
        action="store_true",
        help="If passed then the full book data will be returned for search results",
    )
    # mutual exclusive args, generally for single purpose
    group = parser.add_mutually_exclusive_group()

    group.add_argument(
        "-editions",
        "--editions",
        type=str,
        help="Pass openlib work id and return filtered response from editions API.",
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
    return parser


async def main():
    parser = set_arg_parser()

    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    client = Client(email=EMAIL_ADDRESS)
    caller = OpenLibCaller(client=client)

    if args.open_lib_work_id is not None:
        await caller.get_work_id_results(args.open_lib_work_id)
        await client.close_session()
        sys.exit()

    if args.editions is not None:
        await caller.get_editions_only(args.editions)
        await client.close_session()
        sys.exit()

    if args.search:
        results = await caller.search_books(search_query=args.search, limit=args.limit)

    if args.title or args.author:
        await caller.search_books(
            title=args.title, author=args.author, limit=args.limit
        )

    if args.complete:
        await caller.get_complete_books_data(results)

    await client.close_session()


if __name__ == "__main__":
    asyncio.run(main())
