"""Many calls: the concurrent version and the one-by-one baseline."""

import asyncio
from collections.abc import Sequence

import httpx

from async_fanout.fetch import Result, Sleep, fetch_one


async def fan_out(
    client: httpx.AsyncClient,
    urls: Sequence[str],
    *,
    limit: int = 10,
    max_retries: int = 3,
    base_delay: float = 0.5,
    sleep: Sleep = asyncio.sleep,
) -> list[Result]:
    """Fetch every URL with at most `limit` requests in flight at once.

    - Create one asyncio.Semaphore(limit) and use it with `async with`.
    - Start all the work with asyncio.gather. Results come back in the
      same order as urls.
    - Your decision: does the semaphore wrap the whole of fetch_one
      (simple; a call sleeping in backoff keeps its slot) or each single
      attempt (fairer; fetch_one then needs the semaphore passed in)?
      Start with the simple one. You may change signatures to do the other.
    """
    sem = asyncio.Semaphore(limit)  # one semaphore, shared by every call

    async def fetch_limited(url: str) -> Result:
        async with sem:  # wait here until one of the `limit` slots is free
            return await fetch_one(
                client, url, max_retries=max_retries, base_delay=base_delay, sleep=sleep
            )

    tasks = [fetch_limited(url) for url in urls]
    return await asyncio.gather(*tasks)


def fetch_all_sequential(client: httpx.Client, urls: Sequence[str]) -> list[Result]:
    """The baseline: a plain for loop, one request at a time, no retries.

    Must not raise either: catch httpx.HTTPError and return a failed Result.
    """
    results = []
    for url in urls:
        try:
            response = client.get(url)
            response.raise_for_status()
            result = Result(url=url, ok=True, attempts=1, status=response.status_code)
        except httpx.HTTPStatusError as exc:
            # The server answered, but with a 4xx or 5xx.
            result = Result(
                url=url, ok=False, attempts=1, status=exc.response.status_code
            )
        except httpx.HTTPError as exc:
            # No usable answer: timeout, connection error...
            result = Result(url=url, ok=False, attempts=1, error=str(exc))
        results.append(result)
    return results
