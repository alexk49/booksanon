#!/usr/bin/env python3
import asyncio
import argparse
import os
import sys

from dotenv import load_dotenv

import openlib
from client import Client


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
        "-s",
        "--search",
        type=str,
        help="Search query for book results.",
    )
    parser.add_argument(
        "-olwi",
        "--open-lib-work-id",
        type=str,
        help="Pass openlib workid and return response.",
    )
    return parser


async def main():
    parser = set_arg_parser()

    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    if args.open_lib_work_id is not None:
        work_id = args.open_lib_work_id
        url = openlib.get_work_id_url(work_id)
    else:
        search_query = args.search
        title = args.title
        author = args.author

        if search_query:
            url = openlib.get_general_query_url(search_query, limit="20")
        elif title or author:
            url = openlib.get_complex_query_url(title=title, author=author, limit="20")

    """
    client = Client(email=EMAIL_ADDRESS)

    await client.create_session()

    results = await client.fetch_results(url)

    print("results:")
    print(results)

    # work_keys = openlib.get_unique_work_keys(results)
    # print(work_keys)

    await client.close_session()
    """
    async with Client(email=EMAIL_ADDRESS) as client:
        results = await client.fetch_results(url)
        print(results)



asyncio.run(main())
