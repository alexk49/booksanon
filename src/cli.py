#!/usr/bin/env python3
import asyncio
import argparse
import os
import subprocess
import sys

from dotenv import load_dotenv

from calls.cli import define_call_args, call_open_lib, call_google_books
from db.cli import define_db_args, handle_db_args


def set_arg_parser():
    parser = argparse.ArgumentParser(description="Booksanon cli")
    subparsers = parser.add_subparsers(dest="command", required=True)

    call_parser = subparsers.add_parser("call", help="Call the book search APIs")
    define_call_args(call_parser)

    db_parser = subparsers.add_parser("db", help="db queries")
    define_db_args(db_parser)

    subparsers.add_parser("lint", help="Run project linters")

    subparsers.add_parser("test", help="Run project tests")

    return parser


def run_command(command, check=True):
    try:
        print(f"Running: {' '.join(command)}")
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {' '.join(command)}: {e}")
        sys.exit(e.returncode)


def run_py_linters():
    run_command(["ruff", "check", ".", "--fix"])

    run_command(["ruff", "format", "."])

    run_command(["mypy", "."])


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

    if args.command == "test":
        run_command([sys.executable, "-m", "unittest", "discover", "-v"])


def main():
    """
    Provide syncronous entry point for setuptools etc.
    """
    exit_code = asyncio.run(async_main())

    if exit_code is not None and isinstance(exit_code, int):
        sys.exit(exit_code)


if __name__ == "__main__":
    main()
