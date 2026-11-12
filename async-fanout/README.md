# async-fanout

Calls a public API 100 times, at most 10 at once, with a timeout and retries on every call, then compares the total time with a one-by-one version. Built for module M0 of my AI engineering curriculum (P0: "async fan-out script").

## Usage

```bash
uv sync
uv run fanout
```

A run on 2026-11-12 against JSONPlaceholder (`/posts/1` to `/posts/100`):

```
sequential: 100 calls in 22.10s, 100 ok, 0 failed
concurrent: 100 calls in 2.48s, 100 ok, 0 failed
concurrent was 8.9x faster
```

The speed-up is close to 10x because at most 10 requests are in flight at once. The exit code is 0 if every call succeeded, otherwise 1.

## Checks

```bash
uv run ruff check .
uv run mypy .        # strict mode, configured in pyproject.toml
uv run pytest
```

## Design

| File | Job |
|---|---|
| `src/async_fanout/fetch.py` | `Result` and `fetch_one`: one call with a timeout, retries and backoff; never raises |
| `src/async_fanout/runner.py` | `fan_out` (many calls, limited by a semaphore) and `fetch_all_sequential` (the baseline) |
| `src/async_fanout/cli.py` | `main`: time both versions and print the report |

The main decisions:

- **A failure is a value, not an exception.** `fetch_one` always returns a `Result`, so one bad call can't take down the other 99.
- **Only temporary failures are retried.** Timeouts, connection errors, 429 and 5xx get up to 3 retries (4 requests in total). Other statuses, such as 404, fail at once.
- **Backoff is exponential with jitter.** The wait is `base * 2**attempt` plus a random extra, so failing calls don't all retry at the same instant.
- **The semaphore wraps the whole call.** A call waiting in backoff keeps its slot. That is the simple option; wrapping each attempt would be fairer.
- **No test touches the network or really waits.** Tests use `httpx.MockTransport` and pass in a fake `sleep`.

See [AI_TOOLING_LOG.md](AI_TOOLING_LOG.md) for how AI assistants were used.
