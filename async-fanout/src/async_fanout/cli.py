"""Run both versions against the real API and print the comparison."""

import asyncio
import time
from collections.abc import Sequence

import httpx

from async_fanout.fetch import Result
from async_fanout.runner import fan_out, fetch_all_sequential

BASE_URL = "https://jsonplaceholder.typicode.com/posts"
N_CALLS = 100
LIMIT = 10
TIMEOUT_SECONDS = 5.0


def build_urls(n: int = N_CALLS) -> list[str]:
    """BASE_URL/1 ... BASE_URL/n."""
    return [f"{BASE_URL}/{i}" for i in range(1, n + 1)]


def summarise(label: str, results: Sequence[Result], seconds: float) -> str:
    """One report line, e.g. 'concurrent: 100 calls in 1.42s, 100 ok, 0 failed'."""
    ok = sum(1 for r in results if r.ok)
    failed = len(results) - ok
    return f"{label}: {len(results)} calls in {seconds:.2f}s, {ok} ok, {failed} failed"


async def run_concurrent(urls: Sequence[str]) -> tuple[list[Result], float]:
    """Open one httpx.AsyncClient(timeout=TIMEOUT_SECONDS), call fan_out,
    and time it with time.perf_counter(). Returns (results, seconds).
    """
    async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
        start = time.perf_counter()
        results = await fan_out(client, urls, limit=LIMIT)
        seconds = time.perf_counter() - start
    return results, seconds


def run_sequential(urls: Sequence[str]) -> tuple[list[Result], float]:
    """The same with httpx.Client and fetch_all_sequential."""
    with httpx.Client(timeout=TIMEOUT_SECONDS) as client:
        start = time.perf_counter()
        results = fetch_all_sequential(client, urls)
        seconds = time.perf_counter() - start
    return results, seconds


def main() -> int:
    """Run sequential, then concurrent (asyncio.run), print both summaries
    and how many times faster the concurrent one was.
    Return 0 if every call succeeded, otherwise 1.
    """
    urls = build_urls()

    seq_results, seq_seconds = run_sequential(urls)
    print(summarise("sequential", seq_results, seq_seconds))

    # asyncio.run starts the event loop, runs the coroutine to the end, and
    # hands back its return value. It is the bridge from sync code to async.
    conc_results, conc_seconds = asyncio.run(run_concurrent(urls))
    print(summarise("concurrent", conc_results, conc_seconds))

    print(f"concurrent was {seq_seconds / conc_seconds:.1f}x faster")

    return 0 if all(r.ok for r in seq_results + conc_results) else 1
