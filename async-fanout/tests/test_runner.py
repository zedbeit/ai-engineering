"""Tests for fan_out and fetch_all_sequential. No network."""

import asyncio

import httpx

from async_fanout.fetch import Result
from async_fanout.runner import fan_out, fetch_all_sequential

URLS = [f"https://example.test/posts/{i}" for i in range(1, 31)]


async def fake_sleep(seconds: float) -> None:
    """Stands in for asyncio.sleep so tests finish instantly."""


# --- worked example ---------------------------------------------------------


async def test_one_result_per_url_in_order() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        results = await fan_out(client, URLS, limit=10, sleep=fake_sleep)

    assert [r.url for r in results] == URLS
    assert all(r.ok for r in results)


# --- yours to write ---------------------------------------------------------


async def test_never_more_than_limit_in_flight() -> None:
    """The important one: proves the semaphore really limits concurrency."""
    in_flight = 0  # requests inside the handler right now
    peak = 0  # the most there has ever been at once

    async def handler(request: httpx.Request) -> httpx.Response:
        nonlocal in_flight, peak
        in_flight += 1
        peak = max(peak, in_flight)
        await asyncio.sleep(0.01)  # a real pause, so that requests overlap
        in_flight -= 1
        return httpx.Response(200)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        await fan_out(client, URLS, limit=10, sleep=fake_sleep)

    assert peak <= 10  # the limit held
    assert peak > 1  # and the calls really did run at the same time


async def test_one_failure_does_not_stop_the_rest() -> None:
    """One URL always returns 500: 29 results are ok, 1 is not, nothing raises."""
    bad_url = URLS[4]

    def handler(request: httpx.Request) -> httpx.Response:
        if str(request.url) == bad_url:
            return httpx.Response(500)
        return httpx.Response(200)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        results = await fan_out(client, URLS, limit=10, sleep=fake_sleep)

    assert len(results) == len(URLS)
    failed = [r for r in results if not r.ok]
    assert failed == [Result(url=bad_url, ok=False, attempts=4, status=500)]


async def test_empty_list() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        results = await fan_out(client, [], limit=10, sleep=fake_sleep)

    assert results == []


def test_sequential_one_result_per_url() -> None:
    """Uses httpx.Client(transport=httpx.MockTransport(handler)), no async."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200)

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        results = fetch_all_sequential(client, URLS)

    assert [r.url for r in results] == URLS
    assert all(r.ok and r.attempts == 1 for r in results)


def test_sequential_failure_is_a_result_not_an_exception() -> None:
    """A bad status and a dead connection both come back as failed Results."""
    bad_status_url, dead_url = URLS[0], URLS[1]

    def handler(request: httpx.Request) -> httpx.Response:
        if str(request.url) == bad_status_url:
            return httpx.Response(500)
        if str(request.url) == dead_url:
            raise httpx.ConnectError("down", request=request)
        return httpx.Response(200)

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        results = fetch_all_sequential(client, URLS[:3])

    assert results == [
        Result(url=bad_status_url, ok=False, attempts=1, status=500),
        Result(url=dead_url, ok=False, attempts=1, error="down"),
        Result(url=URLS[2], ok=True, attempts=1, status=200),
    ]
