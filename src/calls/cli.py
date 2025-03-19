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
    return parser


async def main():
    parser = set_arg_parser()

    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    search_query = args.search
    title = args.title
    author = args.author

    client = Client()

    if search_query:
        search_url = openlib.get_general_query_url(search_query, limit="20")
    else:
        search_url = openlib.get_complex_query_url(title=title, author=author, limit="20")

    await client.create_session()

    results = await client.fetch_results(search_url)

    print("results:")
    print(results)

    await client.close_session()


asyncio.run(main())
