#!/usr/bin/env python3
import asyncio
import argparse
import os
import sys

from dotenv import load_dotenv

from calls.cli import define_call_args, call_open_lib, call_google_books
from db.cli import define_db_args, handle_db_args
from utils import run_command


def set_arg_parser():
    parser = argparse.ArgumentParser(description="Booksanon cli")

    subparsers = parser.add_subparsers(dest="command", required=True)

    call_parser = subparsers.add_parser("call", help="Call the book search APIs")
    define_call_args(call_parser)

    db_parser = subparsers.add_parser("db", help="db queries")
    define_db_args(db_parser)

    subparsers.add_parser("lint", help="Run project linters")

    test_parser = subparsers.add_parser("test", help="Run project tests")
    define_test_args(test_parser)

    return parser


def define_test_args(test_parser):
    test_parser.add_argument(
    "--coverage",
        "-c",
        action="store_true",
        help="Run tests with coverage report",
    )

def run_py_linters():
    run_command(["ruff", "check", ".", "--fix"])

    run_command(["ruff", "format", "."])

    run_command(["mypy", "."])


def run_js_linters():
    run_command(["npm", "run", "lint"])

    run_command(["npm", "run", "format"])


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
        await handle_db_args(args)
    if args.command == "lint":
        run_py_linters()

        run_js_linters()

    if args.command == "test":
        if args.coverage:
            run_command(["coverage", "run", "-m", "pytest"])
            run_command(["coverage", "html"])
            sys.exit()
       
        run_command(["pytest"])


def main():
    """
    Provide syncronous entry point for setuptools etc.
    """
    exit_code = asyncio.run(async_main())

    if exit_code is not None and isinstance(exit_code, int):
        sys.exit(exit_code)


if __name__ == "__main__":
    main()
