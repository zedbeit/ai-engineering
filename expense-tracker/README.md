# expense-tracker

A typed command-line expense tracker backed by SQLite. Built for module M0 of my AI engineering curriculum (P0: "rebuild a small tool in idiomatic typed Python, mypy clean, pytest").

## Usage

```bash
uv sync

uv run expense add 12.50 food --date 2026-11-10 --description "lunch"
uv run expense add 3.20 transport            # --date defaults to today
uv run expense list
uv run expense summary --month 2026-11
uv run expense delete 3
```

Data is stored in `~/.expense-tracker.db`.

Bad input never shows a traceback: it prints `error: ...` to stderr and exits with code 1. Unknown commands or missing arguments exit with code 2 (argparse).

## Checks

```bash
uv run ruff check .
uv run mypy .        # strict mode, configured in pyproject.toml
uv run pytest
```

## Design

The code is in three layers, each tested on its own:

| File | Job |
|---|---|
| `src/expense_tracker/models.py` | The frozen `Expense` dataclass and all input parsing and validation |
| `src/expense_tracker/storage.py` | `ExpenseStore`: add, list, delete and monthly summary in SQLite |
| `src/expense_tracker/cli.py` | argparse subcommands; `main(argv, db_path) -> int` |

The main decisions:

- **SQLite over JSON.** Delete by id and filter by month are one query each, and `sqlite3` is in the standard library.
- **Money is never a float.** It's `Decimal` in Python and whole cents (`INTEGER`) in the database.
- **Validation lives in one place.** `Expense.__post_init__` and the `parse_*` functions reject bad data, so the rest of the program can trust it.
- **Everything is injectable for tests.** `ExpenseStore(path)` and `main(argv, db_path)` let tests use pytest's `tmp_path` and never touch real data.

See [AI_TOOLING_LOG.md](AI_TOOLING_LOG.md) for how AI assistants were used.
