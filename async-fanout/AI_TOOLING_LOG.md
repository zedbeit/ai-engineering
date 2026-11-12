# AI-tooling log

How AI assistants were used on this project, what they produced and how their output was checked.

## 2026-11-12: skeleton

Tool: Claude Code in the terminal.

### What the AI did

- **Plan and skeleton.** Claude proposed the design (three layers, a `Result` that is returned instead of raised, an injectable `sleep`) and generated the skeleton: function signatures, type hints, test names, and one worked example test per file. Every function body was `raise NotImplementedError`.

- **Fixing bugs in my `fetch.py` and `test_fetch.py`.** I asked Claude Code to apply the fixes from its review, and it edited my files directly.
  - In `fetch_one`: `attempts` was never incremented (an endless loop on repeated timeouts); a retryable 500 returned straight after its first backoff instead of retrying; `response.status` instead of `status_code`; catching `HTTPError` instead of `HTTPStatusError`; `from random import random` instead of `import random`.
  - In the tests: `async with` inside a plain `def` (a syntax error that stopped the whole file loading); `parametrize` on nested functions that never ran; an exact-equality check on delays that include random jitter; expecting 1 attempt for a timeout that is retried; counters that were never asserted. Claude rewrote `test_is_retryable_status` and `test_backoff_delay_grows_with_attempt`.
- **Fixing bugs in my `runner.py`.** Again applied by Claude Code from its review. In `fan_out`: I created a new `AsyncClient` that shadowed the one passed in; there was no semaphore (Claude added it and the inner `fetch_limited`); `fetch_one` wasn't imported. `fetch_all_sequential` used `await` in a plain `def` and called the async `fetch_one`; Claude rewrote its body with a sync `client.get` and `try/except`.
- **All of `tests/test_runner.py`.** I asked Claude Code to write the five remaining runner tests; I wrote none of that file.
- **Fixing bugs in my `cli.py`.** Applied by Claude Code: `fan_out` and `fetch_all_sequential` imported from the wrong module; `run_*` used a `client` that didn't exist (the clients are now opened inside them); `async with` and `await` inside the plain `def main` (replaced by `asyncio.run`); the limit wasn't passed; the speed-up line was missing.

### What I wrote

- First drafts of `is_retryable_status`, `backoff_delay` and `fetch_one`.
- The `gather` half of `fan_out` (one coroutine per URL, results awaited and returned).
- `build_urls` and `summarise` (unchanged), and first drafts of `run_sequential`, `run_concurrent` and `main`.
- First drafts of the seven async tests in `test_fetch.py`; five of them needed no change or only an added assert.

### How the output was checked

- (fill in as you go)

### What I rejected or changed

- (fill in as you go)
