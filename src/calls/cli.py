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


async def get_work_id_results_only(work_id: str):
    url = openlib.get_work_id_url(work_id)

    async with Client(email=EMAIL_ADDRESS) as client:
        response = await client.fetch_results(url)
        book = openlib.parse_work_id_page(response)
        pprint.pp(book)
        return response


async def get_editions_only(work_id: str):
    url = openlib.get_editions_url(work_id)

    async with Client(email=EMAIL_ADDRESS) as client:
        response = await client.fetch_results(url)
        pprint.pp(response)
        return response


async def make_complex_query_search(args) -> list:
    """ Complex queries specify each parameter in order to get better results. The results are limited by the URL parameter """
    title = args.title
    author = args.author
    limit = args.limit

    url = openlib.get_complex_query_url(title=title, author=author, limit=limit)

    async with Client(email=EMAIL_ADDRESS) as client:
        results = await client.fetch_results(url)

        clean_results = openlib.process_books_search_results(results) 

        complete_books = []

        for book in clean_results:
            complete_books.append(await get_complete_book_data(client, book))

        pprint.pp(complete_books)
        return complete_books


async def make_general_query_search(search_query, limit) -> list:
    """ General query searches can't be limited with results, so the results returned are sliced with the limit """
    url = openlib.get_general_query_url(search_query, limit=1)

    async with Client(email=EMAIL_ADDRESS) as client:
        results = await client.fetch_results(url)
        clean_results = openlib.process_books_search_results(results, limit=limit) 

        complete_books = []

        for book in clean_results:
            complete_books.append(await get_complete_book_data(client, book))

        pprint.pp(complete_books)
        return complete_books


async def get_complete_book_data(client: Client, book: dict) -> dict:
    """ helper function to be used inside a loop """
    work_id = book["openlib_work_key"]
    url = openlib.get_work_id_url(work_id)

    response = await client.fetch_results(url)

    book = (openlib.parse_work_id_page(response, book=book))
    url = openlib.get_editions_url(work_id)
    response = await client.fetch_results(url)
    return openlib.parse_editions_response(response=response, book=book)


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

    if args.search:
        await make_general_query_search(args.search, limit=args.limit)
        sys.exit()
    else:
        await make_complex_query_search(args)


asyncio.run(main())
