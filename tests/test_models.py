from datetime import date
from decimal import Decimal

import pytest

from expense_tracker.models import (
    Expense,
    from_cents,
    parse_amount,
    parse_date,
    parse_month,
    to_cents,
)


def test_parse_amount_valid() -> None:
    assert parse_amount("12.50") == Decimal("12.50")


def test_parse_amount_rejects_negative() -> None:
    with pytest.raises(ValueError, match="Amount cannot be negative"):
        parse_amount("-1")


def test_parse_amount_rejects_text() -> None:
    with pytest.raises(ValueError, match="Invalid amount"):
        parse_amount("abc")


def test_parse_amount_rejects_nan() -> None:
    with pytest.raises(ValueError, match="Invalid amount"):
        parse_amount("NaN")


def test_parse_amount_rejects_three_decimal_places() -> None:
    with pytest.raises(ValueError, match="more than 2 decimal places"):
        parse_amount("1.234")


def test_parse_date_valid() -> None:
    assert parse_date("2026-11-30") == date(2026, 11, 30)


def test_parse_date_rejects_impossible_day() -> None:
    with pytest.raises(ValueError, match="Invalid date format"):
        parse_date("2026-11-31")


def test_parse_date_rejects_impossible_month() -> None:
    with pytest.raises(ValueError, match="Invalid date format"):
        parse_date("2026-13-01")


def test_parse_date_rejects_wrong_format() -> None:
    with pytest.raises(ValueError, match="Invalid date format"):
        parse_date("10/11/2026")


def test_parse_month_valid() -> None:
    assert parse_month("2026-11") == (2026, 11)


def test_parse_month_rejects_bad_month() -> None:
    with pytest.raises(ValueError, match="Month must be between 1 and 12"):
        parse_month("2026-13")

    with pytest.raises(ValueError, match="Invalid month format"):
        parse_month("Nov")


def test_cents_round_trip() -> None:
    assert from_cents(to_cents(Decimal("12.34"))) == Decimal("12.34")


def test_expense_rejects_negative_amount() -> None:
    with pytest.raises(ValueError, match="Amount cannot be negative"):
        Expense(Decimal("-1"), "food", date(2026, 11, 10))


def test_expense_rejects_zero_amount() -> None:
    with pytest.raises(ValueError, match="Amount cannot be zero"):
        Expense(Decimal("0"), "food", date(2026, 11, 10))


def test_expense_rejects_blank_category() -> None:
    with pytest.raises(ValueError, match="Category cannot be empty"):
        Expense(Decimal("1"), "   ", date(2026, 11, 10))
