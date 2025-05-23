#!/usr/bin/env python3
import asyncio
import argparse
import os
import sys

from dotenv import load_dotenv

from calls.cli import define_call_args, call_open_lib, call_google_books
from db.cli import define_db_args, create_schema


def set_arg_parser():
    parser = argparse.ArgumentParser(description="Booksanon cli")
    subparsers = parser.add_subparsers(dest="command", required=True)

    call_parser = subparsers.add_parser("call", help="Call the book search APIs")
    define_call_args(call_parser)

    db_parser = subparsers.add_parser("db", help="db queries")
    define_db_args(db_parser)

    return parser


async def async_main():
    parser = set_arg_parser()
    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    load_dotenv()

    if args.command == "call":
        EMAIL_ADDRESS = os.environ.get("EMAIL_ADDRESS", "")

        if args.api == "openlibrary" or args.api == "ol":
            if not EMAIL_ADDRESS:
                print("email not set, this is needed for openlib calls.")
                sys.exit()
            await call_open_lib(args, EMAIL_ADDRESS)

        elif args.api == "googlebooks" or args.api == "gb":
            await call_google_books(args)

    if args.command == "db":
        POSTGRES_USERNAME = os.environ.get("POSTGRES_USERNAME", "")
        POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "")
        POSTGRES_URL = os.environ.get("POSTGRES_URL", "")

        if args.create_schema:
            await create_schema(user=POSTGRES_USERNAME, password=POSTGRES_PASSWORD, url=POSTGRES_URL)


def main():
    """
    Provide syncronous entry point for setuptools etc.
    """
    exit_code = asyncio.run(async_main())

    if exit_code is not None and isinstance(exit_code, int):
        sys.exit(exit_code)


if __name__ == "__main__":
    main()
