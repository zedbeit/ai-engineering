import asyncio
import random
from collections.abc import Awaitable, Callable
from dataclasses import dataclass

import httpx

# The type of asyncio.sleep: takes seconds, returns something you can await.
# Tests pass a fake with the same shape so they never really wait.
Sleep = Callable[[float], Awaitable[None]]


@dataclass(frozen=True)
class Result:
    url: str
    ok: bool
    attempts: int  # how many requests were actually sent (1 = no retries)
    status: int | None = None  # the last HTTP status, or None if no response came
    error: str | None = None  # a short reason when ok is False


def is_retryable_status(status: int) -> bool:
    if status == 429 or 500 <= status < 600:
        return True
    return False


def backoff_delay(attempt: int, base_delay: float) -> float:
    return base_delay * 2.0**attempt + random.uniform(0, base_delay)


async def fetch_one(
    client: httpx.AsyncClient,
    url: str,
    *,
    max_retries: int = 3,
    base_delay: float = 0.5,
    sleep: Sleep = asyncio.sleep,
) -> Result:
    attempts = 0  # failed tries so far; the try in progress is number attempts + 1
    while True:
        try:
            response = await client.get(url)
            response.raise_for_status()
            return Result(
                url=url, ok=True, attempts=attempts + 1, status=response.status_code
            )
        except httpx.HTTPStatusError as exc:
            status = exc.response.status_code
            if not is_retryable_status(status) or attempts == max_retries:
                return Result(url=url, ok=False, attempts=attempts + 1, status=status)
        except (httpx.TimeoutException, httpx.TransportError) as exc:
            if attempts == max_retries:
                return Result(url=url, ok=False, attempts=attempts + 1, error=str(exc))
        # Only a retryable failure with retries left reaches this point.
        await sleep(backoff_delay(attempts, base_delay))
        attempts += 1
