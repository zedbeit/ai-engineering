from collections.abc import Iterator
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from expense_tracker.models import Expense
from expense_tracker.storage import ExpenseStore


@pytest.fixture
def store(tmp_path: Path) -> Iterator[ExpenseStore]:
    """A fresh database in a temp folder for every test. Never your real data."""
    s = ExpenseStore(tmp_path / "test.db")
    yield s
    s.close()


def test_add_then_list(store: ExpenseStore) -> None:
    saved = store.add(Expense(Decimal("12.50"), "food", date(2026, 11, 10)))
    assert saved.id is not None
    assert store.list_all() == [saved]


def test_list_empty(store: ExpenseStore) -> None:
    assert store.list_all() == []


def test_data_survives_reopening(tmp_path: Path) -> None:
    store1 = ExpenseStore(tmp_path / "test.db")
    store1.add(Expense(Decimal("12.50"), "food", date(2026, 11, 10)))
    store1.close()

    store2 = ExpenseStore(tmp_path / "test.db")
    assert store2.list_all() == [
        Expense(Decimal("12.50"), "food", date(2026, 11, 10), id=1)
    ]
    store2.close()


def test_summary_only_counts_that_month(store: ExpenseStore) -> None:
    store.add(Expense(Decimal("12.50"), "food", date(2026, 10, 31)))
    store.add(Expense(Decimal("15.00"), "food", date(2026, 11, 1)))
    store.add(Expense(Decimal("5.00"), "transport", date(2026, 11, 30)))
    store.add(Expense(Decimal("9.99"), "food", date(2026, 12, 1)))
    assert store.summary(2026, 10) == {"food": Decimal("12.50")}
    assert store.summary(2026, 11) == {
        "food": Decimal("15.00"),
        "transport": Decimal("5.00"),
    }


def test_summary_groups_by_category(store: ExpenseStore) -> None:
    store.add(Expense(Decimal("12.50"), "food", date(2026, 11, 10)))
    store.add(Expense(Decimal("15.00"), "food", date(2026, 11, 11)))
    store.add(Expense(Decimal("5.00"), "transport", date(2026, 11, 12)))
    assert store.summary(2026, 11) == {
        "food": Decimal("27.50"),
        "transport": Decimal("5.00"),
    }


def test_delete_existing(store: ExpenseStore) -> None:
    expense = store.add(Expense(Decimal("12.50"), "food", date(2026, 11, 10)))
    assert expense.id is not None
    assert store.delete(expense.id)
    assert store.list_all() == []


def test_delete_missing_returns_false(store: ExpenseStore) -> None:
    assert not store.delete(999)
