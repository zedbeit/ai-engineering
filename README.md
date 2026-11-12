# ai-engineering

My work for a self-directed AI engineering curriculum (~42 weeks, 11 modules). Each project is in its own folder, as a separate uv project with its own `pyproject.toml`, lockfile and tests.

## Projects

| Folder | Module | What it is |
|---|---|---|
| [`expense-tracker/`](expense-tracker/) | M0 · Python for AI engineering | Typed CLI expense tracker: SQLite, dataclasses, `mypy --strict`, ruff, 30 pytest tests |
| [`async-fanout/`](async-fanout/) | M0 · Python for AI engineering | Async fan-out script: 100 API calls with httpx, at most 10 at once (semaphore), timeouts, retries with backoff; 19 pytest tests |

## Working on a project

```bash
cd expense-tracker
uv sync
uv run pytest
```
