# Add `--category` filter to `expense list`

## Context
`expense list` prints every expense. The user wants `list --category food` to show only that category's expenses, with tests, and the whole suite (pytest + ruff + mypy strict) passing.

## Approach: filter in SQL in the storage layer
Keeps the three-layer split (CLI parses → storage queries), matching how `summary` already filters in SQL.

### 1. `src/expense_tracker/storage.py` — `list_all`
- Signature: `def list_all(self, category: str | None = None) -> list[Expense]:`
- If `category is None`: current query unchanged.
- Else: add `WHERE category = ?` with `(category,)` as a parameter (never f-string into SQL), same `ORDER BY spent_on ASC`.
- Row → `Expense` conversion stays as is.
- Exact, case-sensitive match (same as how categories are stored and grouped by `summary`).

### 2. `src/expense_tracker/cli.py`
- `build_parser`: `list_parser = subparsers.add_parser("list")` then `list_parser.add_argument("--category", type=str, default=None)`.
- `cmd_list`: `expenses = store.list_all(args.category)`. Empty-result message:
  - no filter → `"No expenses yet."` (unchanged, existing test relies on behaviour)
  - with filter → `f"No expenses in category {args.category}."`

### 3. Tests
`tests/test_storage.py` (reuse the `store` fixture):
- `test_list_filters_by_category` — add food + rent, `list_all("food")` returns only the food one.
- `test_list_unknown_category_is_empty` — `list_all("travel") == []`.

`tests/test_cli.py` (same `tmp_path`/`capsys` pattern as existing tests):
- `test_list_category_shows_only_that_category` — add food and rent, `capsys.readouterr()` to discard "Added" lines, `main(["list", "--category", "food"])` returns 0, output contains `food`, not `rent`.
- `test_list_category_with_no_matches` — returns 0, prints "No expenses in category travel."
- Existing `test_add_then_list_shows_expense` covers the no-flag path still working.

### 4. `README.md` / `AI_TOOLING_LOG.md`
- README: add a `expense list --category food` usage line if a usage section exists.
- Per the curriculum logging habit, append an entry to `AI_TOOLING_LOG.md` stating Claude Code wrote the `--category` feature and its tests (user did not draft this one).

## Verification
From `expense-tracker/`:
```
uv run pytest
uv run ruff check .
uv run mypy .
```
Expect 34 tests passing (30 + 4), ruff and mypy clean. Manual smoke test with a temp DB:
```
uv run python -c "from pathlib import Path; from expense_tracker.cli import main; p=Path('/tmp/et.db'); main(['add','5','food'],db_path=p); main(['add','9','rent'],db_path=p); main(['list','--category','food'],db_path=p)"
```
then delete `/tmp/et.db`.
