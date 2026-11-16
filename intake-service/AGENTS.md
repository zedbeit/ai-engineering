# Intake service

A small FastAPI service that stores text documents in SQLite: create, fetch,
list or search, and delete.

`SPEC.md` is the source of truth for behaviour. Read it before writing any
code. If the spec and a test disagree, or the spec does not cover a case, stop
and ask; do not guess.

## Commands

Run everything from this folder (`intake-service/`).

- `uv run pytest`: run the tests. `uv run pytest tests/test_create.py` runs one
  file.
- `uv run mypy src tests`: type-check, in strict mode.
- `uv run ruff check`: lint.
- `uv run ruff format`: format.
- `uv run uvicorn intake_service.main:app --reload`: run the service locally.

## Hard rules

- **Never edit anything in `tests/`, and never edit `SPEC.md`.** The tests were
  written before the code and are the definition of done. If a test looks
  wrong, say which one and why, and wait.
- **Never make a test pass by special-casing it**, for example by checking for
  the exact values a test sends. Implement the behaviour the spec describes.
- **Do not add dependencies.** FastAPI, Uvicorn and the standard library are
  enough. If you think another package is needed, ask first.

## Code rules

- Type hints on every function, including return types. No `Any` and no
  `# type: ignore` without a comment saying why.
- Database access uses the standard-library `sqlite3` module only. Values go
  into SQL as `?` parameters, never through string formatting.
- Pydantic models for every request and response body.
- Prefer plain, readable code over clever code. Every diff is reviewed by
  someone new to FastAPI, and anything they cannot follow is rejected.

## Layout

- `src/intake_service/main.py`: the FastAPI app, as the object `app`. Tests
  import it from here.
- `src/intake_service/`: all other code.
- `tests/`: pytest tests using `TestClient`. Read-only for you.

## How to work

- One endpoint at a time, starting with `POST /documents`, since every other
  test creates documents first.
- Keep each change small enough to review in one sitting, and say which tests
  it is meant to turn green.

## Done means

All of these pass, with no test skipped or changed:

```
uv run pytest
uv run mypy src tests
uv run ruff check
uv run ruff format --check
```
