import asyncio
from collections.abc import Awaitable, Callable

import httpx


async def request_with_retries(
    make_request: Callable[[], Awaitable[httpx.Response]],
    *,
    retries: int = 2,
    base_backoff_seconds: float = 0.4,
) -> httpx.Response:
    last_exc: Exception | None = None
    for attempt in range(retries + 1):
        try:
            return await make_request()
        except (httpx.TimeoutException, httpx.NetworkError, httpx.RemoteProtocolError) as exc:
            last_exc = exc
            if attempt >= retries:
                raise
            await asyncio.sleep(base_backoff_seconds * (2**attempt))
    raise last_exc or RuntimeError("request failed")
