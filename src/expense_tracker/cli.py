"""Command-line interface: parse arguments, call storage, print results.

This layer turns errors into messages and exit codes. Users should never
see a Python traceback.
"""

import argparse
import sys
from datetime import date
from pathlib import Path

from expense_tracker.models import Expense, parse_amount, parse_date, parse_month
from expense_tracker.storage import ExpenseStore

DEFAULT_DB = Path.home() / ".expense-tracker.db"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Add command
    add_parser = subparsers.add_parser("add")
    add_parser.add_argument("amount", type=str)
    add_parser.add_argument("category", type=str)
    add_parser.add_argument("--date", type=str, default=str(date.today()))
    add_parser.add_argument("--description", type=str, default="")

    # List command
    subparsers.add_parser("list")

    # Summary command
    summary_parser = subparsers.add_parser("summary")
    summary_parser.add_argument("--month", type=str, required=True)

    # Delete command
    delete_parser = subparsers.add_parser("delete")
    delete_parser.add_argument("id", type=int)

    return parser


def cmd_add(store: ExpenseStore, args: argparse.Namespace) -> int:
    expense = Expense(
        amount=parse_amount(args.amount),
        category=args.category,
        spent_on=parse_date(args.date),
        description=args.description,
    )
    saved = store.add(expense)
    print(f"Added expense with id {saved.id}")
    return 0


def cmd_list(store: ExpenseStore, args: argparse.Namespace) -> int:
    expenses = store.list_all()
    if not expenses:
        print("No expenses yet.")
    for expense in expenses:
        print(
            f"{expense.id}: {expense.spent_on} {expense.amount} "
            f"{expense.category} {expense.description}"
        )
    return 0


def cmd_summary(store: ExpenseStore, args: argparse.Namespace) -> int:
    year, month = parse_month(args.month)
    summary = store.summary(year, month)
    if not summary:
        print("No expenses found for this month.")
        return 0
    for category, total in summary.items():
        print(f"{category}: {total}")
    print(f"total: {sum(summary.values())}")
    return 0


def cmd_delete(store: ExpenseStore, args: argparse.Namespace) -> int:
    if store.delete(args.id):
        print(f"Deleted expense with id {args.id}")
        return 0
    else:
        print(f"Expense with id {args.id} not found.", file=sys.stderr)
        return 1


def main(argv: list[str] | None = None, db_path: Path = DEFAULT_DB) -> int:
    args = build_parser().parse_args(argv)
    store = ExpenseStore(db_path)
    try:
        match args.command:
            case "add":
                return cmd_add(store, args)
            case "list":
                return cmd_list(store, args)
            case "summary":
                return cmd_summary(store, args)
            case "delete":
                return cmd_delete(store, args)
            case _:
                raise AssertionError(f"unknown command {args.command!r}")
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    finally:
        store.close()
