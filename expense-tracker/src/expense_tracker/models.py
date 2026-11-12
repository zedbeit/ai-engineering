"""The Expense type and the functions that turn user input into valid values.

Every check on user input lives in this file. If a value gets past here,
the rest of the program can trust it.
"""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation


@dataclass(frozen=True)
class Expense:
    """One expense. Frozen means it can't be changed after it's created."""

    amount: Decimal
    category: str
    spent_on: date
    description: str = ""
    id: int | None = None  # None until the database assigns one

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValueError("Amount cannot be negative")
        elif self.amount == 0:
            raise ValueError("Amount cannot be zero")

        if not self.category.strip():
            raise ValueError("Category cannot be empty")


def parse_amount(text: str) -> Decimal:
    try:
        amount = Decimal(text)
    except InvalidOperation as err:
        raise ValueError("Invalid amount") from err

    exponent = amount.as_tuple().exponent
    if not isinstance(exponent, int):  # NaN or Infinity
        raise ValueError("Invalid amount")

    if amount < 0:
        raise ValueError("Amount cannot be negative")

    if exponent < -2:
        raise ValueError("Amount cannot have more than 2 decimal places")

    return amount


def parse_date(text: str) -> date:
    try:
        return date.fromisoformat(text)
    except ValueError as err:
        raise ValueError("Invalid date format") from err


def parse_month(text: str) -> tuple[int, int]:
    try:
        year, month = map(int, text.split("-"))
    except ValueError as err:
        raise ValueError("Invalid month format") from err

    if not 1 <= month <= 12:
        raise ValueError("Month must be between 1 and 12")
    return year, month


def to_cents(amount: Decimal) -> int:
    return int(amount * 100)


def from_cents(cents: int) -> Decimal:
    return Decimal(cents).scaleb(-2)
