# AI-tooling log

How AI assistants were used on this project, what they produced and how their output was checked.

Format from week 3 on: date | task given to the agent | what it did | what I rejected or changed | why.

## 2026-11-16: SPEC.md breakdown

Tool: Claude Code in the terminal.

### What the AI did

- **Breakdown of `SPEC.md`.** I asked Claude to break down the spec for the intake service. It listed the sections the spec needs and the decisions I have to make in each one (id type, validation limits, search behaviour, status codes, error shape, database location). It did not write any of the spec.
- **Design decisions, made together.** Claude asked eleven multiple-choice questions (id type, title and text rules, search behaviour, list shape, pagination, validation status, extra fields, database location, database library), each with a recommendation. I chose the recommended option every time. Claude also proposed defaults I did not choose between: `201` for create, `204` for delete, `404` body `{"detail": "Document not found"}`, list ordered by id, ids never reused.
- **`SPEC.md` skeleton.** Claude created the headings and wrote section 3.4 (`DELETE /documents/{id}`) in full as a worked example. Everything else was `TODO`.
- **All of `SPEC.md`.** I asked Claude to fill in the whole draft, and it wrote every section from the decisions above; I wrote none of the wording. The curriculum says to write the spec yourself, so this is a departure from it. Claude also added details I had not decided: `text` is stored untrimmed; the timestamp is to the second and ends in `Z`; `%` and `_` in a search term are literal; search ignores case for A to Z only; one database connection per request, with the table created on connect; the app lives at `intake_service.main:app`; tests assert the `422` status and not its wording.
- **Project setup.** Claude ran `uv init --package`, added FastAPI, Uvicorn, pytest, httpx, mypy and ruff, and copied the mypy, ruff and pytest settings from `async-fanout`. It wrote `src/intake_service/main.py` as an empty app (`app = FastAPI()`, no routes) so that the tests fail on behaviour and not on a missing import.
- **Test skeleton.** Claude wrote `tests/conftest.py` (the `db_path` and `client` fixtures) in full, the names of all 31 tests, and six test bodies: one worked example each in `test_create.py`, `test_get.py`, `test_list.py` and `test_delete.py`, the `create` helper in `test_list.py`, and all of `test_persistence.py`. The other 25 bodies are `raise NotImplementedError`. All 31 fail; mypy and ruff pass.
- **All the test bodies.** I asked Claude to fill in the 25 placeholder tests, and it wrote every one; I wrote none of the tests. The curriculum says to write the tests yourself, so this is a second departure from it. Claude also added things I had not asked for: eleven more invalid-input cases (null and non-string values, whitespace-only text), `test_create_rejects_a_body_that_is_not_an_object`, a `search_ids` helper, and a `create` helper in `test_delete.py`. Result: 43 tests, all failing against the empty app because the routes return 404; mypy and ruff pass.
- **`AGENTS.md` and `CLAUDE.md`.** I asked Claude to write the agent instructions after it broke the step down. It wrote all of `AGENTS.md` (commands, "never edit `tests/` or `SPEC.md`", no new dependencies, code rules, layout, working one endpoint at a time, what done means) and a one-line `CLAUDE.md` that imports it. The curriculum lists this as mine to write. Claude added two rules I had not asked for: never special-case a test to make it pass, and no `Any` or `# type: ignore` without a reason.
- **The pytest hook and the permission rule (step 4).** I asked Claude for step 4 and it wrote both without a breakdown first. `.claude/hooks/run-pytest.sh` runs `uv run pytest -q --tb=no` after any edit to a `.py` file and, if tests fail, sends the list of failing tests back to the agent (exit code 2). `.claude/settings.json` registers it as a `PostToolUse` hook on `Write|Edit` and denies edits to `tests/` and `SPEC.md`. Claude checked both in the session: an edit to `main.py` came back with the 43 failures, and an edit to `tests/test_get.py` was refused. The curriculum lists this step as mine.

### What I wrote

### What I rejected or changed, and why
