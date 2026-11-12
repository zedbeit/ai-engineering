"""SQLite storage for expenses.

This layer only talks to the database. It assumes every Expense it receives
is already valid, because models.py checked it.
"""

import dataclasses
import sqlite3
from datetime import date
from decimal import Decimal
from pathlib import Path

from expense_tracker.models import Expense, from_cents, to_cents

SCHEMA = """
CREATE TABLE IF NOT EXISTS expenses (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    amount_cents INTEGER NOT NULL CHECK (amount_cents >= 0),
    category     TEXT    NOT NULL,
    description  TEXT    NOT NULL DEFAULT '',
    spent_on     TEXT    NOT NULL  -- ISO date, e.g. '2026-11-10'
)
"""


class ExpenseStore:
    """Wraps one SQLite database file."""

    def __init__(self, path: Path) -> None:
        self._conn: sqlite3.Connection = sqlite3.connect(path)
        self._conn.execute(SCHEMA)

    def add(self, expense: Expense) -> Expense:
        cursor = self._conn.cursor()
        cursor.execute(
            """
            INSERT INTO expenses (amount_cents, category, description, spent_on)
            VALUES (?, ?, ?, ?)
            """,
            (
                to_cents(expense.amount),
                expense.category,
                expense.description,
                expense.spent_on.isoformat(),
            ),
        )
        new_id = cursor.lastrowid
        self._conn.commit()
        return dataclasses.replace(expense, id=new_id)

    def list_all(self) -> list[Expense]:
        cursor = self._conn.cursor()
        cursor.execute(
            """
            SELECT id, amount_cents, category, description, spent_on
            FROM expenses
            ORDER BY spent_on ASC
            """
        )
        rows = cursor.fetchall()
        return [
            Expense(
                amount=from_cents(amount_cents),
                category=category,
                description=description,
                spent_on=date.fromisoformat(spent_on),
                id=expense_id,
            )
            for expense_id, amount_cents, category, description, spent_on in rows
        ]

    def delete(self, expense_id: int) -> bool:
        cursor = self._conn.cursor()
        cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        self._conn.commit()
        return cursor.rowcount > 0

    def summary(self, year: int, month: int) -> dict[str, Decimal]:
        cursor = self._conn.cursor()
        cursor.execute(
            """
            SELECT category, SUM(amount_cents)
            FROM expenses
            WHERE spent_on LIKE ?
            GROUP BY category
            """,
            (f"{year}-{month:02}-%",),
        )
        rows = cursor.fetchall()
        return {category: from_cents(total) for category, total in rows}

    def close(self) -> None:
        self._conn.close()
