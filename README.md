# ai-engineering

My work for a self-directed AI engineering curriculum (~42 weeks, 11 modules). Each project is in its own folder, as a separate uv project with its own `pyproject.toml`, lockfile and tests.

## Projects

| Folder | Module | What it is |
|---|---|---|
| [`expense-tracker/`](expense-tracker/) | M0 · Python for AI engineering | Typed CLI expense tracker: SQLite, dataclasses, `mypy --strict`, ruff, 30 pytest tests |

## Working on a project

```bash
cd expense-tracker
uv sync
uv run pytest
```
