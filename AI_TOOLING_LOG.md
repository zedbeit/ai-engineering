# AI-tooling log

How AI assistants were used on this project, what they produced and how their output was checked.

## 2026-11-10 to 2026-11-12: first version

Tools: Claude in the claude.ai chat (planning and skeleton), then Claude Code in the terminal (explanations, review and fixes).

### What the AI did

- **Plan and skeleton.** Claude proposed the design (SQLite, `Decimal` and cents, three layers, injectable paths) and generated the skeleton: function signatures, type hints, the SQLite schema, test names, and one worked example test per file. Every function body was `raise NotImplementedError`.
- **Explanations.** I asked about `@dataclass(frozen=True)`, `int | None`, `__post_init__`, `Decimal.as_tuple()`, `map`, `raise ... from err`, imports, `sqlite3`, the `_` naming convention, list comprehensions, f-string format specs, pytest fixtures and argparse.
- **Fixing bugs in my models and storage code.** I asked Claude Code to fix failing tests, and it edited my files directly. The fixes were: `self.` missing in `__post_init__`; catching `InvalidOperation` and `ValueError` instead of `Exception` or `AttributeError`; a NaN crash; a backwards check in `to_cents`; `from_cents` returning `12.5` instead of `12.50`; missing imports in `storage.py`; long SQL lines; and test bugs (a non-existent date, `date(...)`, missing imports, a mypy `int | None` error).
- **Most of the CLI layer.** I wrote the argparse parser and first drafts of the `cmd_*` functions and `main`. Claude Code fixed six bugs in them and **wrote all of `tests/test_cli.py`**. The bugs were: missing imports; `Decimal()` bypassing `parse_amount`; the wrong field name (`date` instead of `spent_on`); printing the unsaved id; treating `parse_month`'s tuple as an object; and no default `case` in `match`.

### What I wrote

- First drafts of `models.py` (`__post_init__` and the `parse_*` functions) and of the model tests.
- First drafts of every `storage.py` method and the storage tests.
- `build_parser` and first drafts of the CLI functions.

### How the output was checked

- Every change was run against `uv run pytest`, `uv run ruff check .` and `uv run mypy .` (strict). The final state is 30 tests passing with both checks clean.
- Claude Code also tested its own claims by running them: what `Decimal` tuples look like, mypy's behaviour on `as_tuple().exponent`, and argparse with `-5`.
- It corrected two of its own mistakes along the way. `is_finite()` doesn't satisfy mypy, so an `isinstance` check is needed. And `lastrowid` being `int | None` turned out not to be a mypy error.

### What I rejected or changed

- Kept zero as an invalid amount (my decision, now covered by a test).

### Lessons and follow-ups

- The bugs Claude found were mostly ones that hadn't run yet: Python only fails on a line when it executes it. Running the tests after each small change catches them sooner.
- **To do:** rewrite `cli.py` and `tests/test_cli.py` from memory without AI, since Claude wrote most of the final version of that layer.
