#!/usr/bin/env python3
import asyncio
import argparse
import os
import pprint
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
        "-editions",
        "--editions",
        type=str,
        help="Pass openlib work id and return filtered response from editions API.",
    )
    parser.add_argument(
        "-l",
        "--limit",
        default=5,
        type=int,
        help="Limit number of results that come back",
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
        help="Pass openlib work id and return response.",
    )
    return parser


async def get_work_id_results_only(work_id):
    url = openlib.get_work_id_url(work_id)

    async with Client(email=EMAIL_ADDRESS) as client:
        response = await client.fetch_results(url)
        pprint.pp(response)
        print(type(response))
        book = openlib.parse_work_id_page(response)
        pprint.pp(book)


async def get_editions_only(work_id):
    url = openlib.get_work_id_url(work_id, editions=True)

    async with Client(email=EMAIL_ADDRESS) as client:
        response = await client.fetch_results(url)
        pprint.pp(response)


async def main():
    parser = set_arg_parser()

    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    if args.open_lib_work_id is not None:
        await get_work_id_results_only(args.open_lib_work_id)
        sys.exit()

    if args.editions is not None:
        await get_editions_only(args.editions)
        sys.exit()

    limit = str(args.limit)

    if args.search:
        url = openlib.get_general_query_url(args.search, limit=limit)
    else:
        title = args.title
        author = args.author
        url = openlib.get_complex_query_url(title=title, author=author, limit=limit)

    async with Client(email=EMAIL_ADDRESS) as client:
        results = await client.fetch_results(url)

        pprint.pp(results)

        clean_results = openlib.process_books_search_results(results) 

        pprint.pp(clean_results)

        complete_books = []

        for book in clean_results:
            work_id = book["openlib_work_key"]
            url = openlib.get_work_id_url(work_id)
            response = await client.fetch_results(url)

            complete_books.append(openlib.parse_work_id_page(response, book=book))

        pprint.pp(complete_books)


asyncio.run(main())
