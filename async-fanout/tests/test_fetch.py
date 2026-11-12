import httpx
import pytest

from async_fanout.fetch import Result, backoff_delay, fetch_one, is_retryable_status

URL = "https://example.test/posts/1"


async def fake_sleep(seconds: float) -> None:
    pass


# --- worked example ---------------------------------------------------------


async def test_success_first_try() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"id": 1})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        result = await fetch_one(client, URL, sleep=fake_sleep)

    assert result == Result(url=URL, ok=True, attempts=1, status=200)


# --- yours to write ---------------------------------------------------------


async def test_retries_then_succeeds() -> None:
    counter = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal counter
        counter += 1
        if counter < 3:
            return httpx.Response(500)
        return httpx.Response(200, json={"id": 1})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        result = await fetch_one(client, URL, sleep=fake_sleep)

    assert result == Result(url=URL, ok=True, attempts=3, status=200)


async def test_gives_up_after_max_retries() -> None:
    counter = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal counter
        counter += 1
        return httpx.Response(500)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        result = await fetch_one(client, URL, sleep=fake_sleep, max_retries=3)

    assert result == Result(url=URL, ok=False, attempts=4, status=500)
    assert counter == 4


async def test_404_is_not_retried() -> None:
    counter = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal counter
        counter += 1
        return httpx.Response(404)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        result = await fetch_one(client, URL, sleep=fake_sleep)

    assert result == Result(url=URL, ok=False, attempts=1, status=404)
    assert counter == 1


async def test_timeout_is_retried() -> None:
    counter = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal counter
        counter += 1
        if counter == 1:
            raise httpx.ReadTimeout("slow", request=request)
        return httpx.Response(200, json={"id": 1})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        result = await fetch_one(client, URL, sleep=fake_sleep)

    assert result == Result(url=URL, ok=True, attempts=2, status=200)


async def test_timeout_every_time_returns_failure_not_exception() -> None:
    counter = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal counter
        counter += 1
        raise httpx.ReadTimeout("slow", request=request)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        result = await fetch_one(client, URL, sleep=fake_sleep)

    assert result == Result(url=URL, ok=False, attempts=4, status=None, error="slow")
    assert counter == 4


async def test_sleeps_between_tries_and_delays_grow() -> None:
    delays: list[float] = []

    async def sleep(seconds: float) -> None:
        delays.append(seconds)

    counter = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal counter
        counter += 1
        if counter < 3:
            return httpx.Response(500)
        return httpx.Response(200, json={"id": 1})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        result = await fetch_one(client, URL, sleep=sleep)

    assert result == Result(url=URL, ok=True, attempts=3, status=200)
    assert len(delays) == 2
    assert delays[1] > delays[0]


@pytest.mark.parametrize(
    ("status", "expected"),
    [(429, True), (500, True), (503, True), (400, False), (404, False)],
)
def test_is_retryable_status(status: int, expected: bool) -> None:
    assert is_retryable_status(status) is expected


def test_backoff_delay_grows_with_attempt() -> None:
    base = 0.5
    for attempt in range(4):
        lowest = base * 2**attempt
        assert lowest <= backoff_delay(attempt, base) <= lowest + base
