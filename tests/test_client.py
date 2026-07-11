from unittest.mock import AsyncMock, call

import httpx
import pytest

from src.client import CaptureError, PaymentClient


def response(status_code: int) -> httpx.Response:
    return httpx.Response(
        status_code,
        json={
            "id": "cap_123",
            "metadata": {"order_id": "order_123"},
            "status": "captured",
        },
    )


@pytest.mark.asyncio
async def test_capture_retries_with_backoff_and_idempotency_key(monkeypatch):
    client = PaymentClient("test-key")
    post = AsyncMock(side_effect=[response(500), response(429), response(200)])
    sleep = AsyncMock()
    monkeypatch.setattr(client, "_post", post)
    monkeypatch.setattr("src.client.asyncio.sleep", sleep)

    try:
        result = await client.capture("order_123", 2500)
    finally:
        await client._http.aclose()

    assert result.capture_id == "cap_123"
    assert post.await_count == 3
    assert sleep.await_args_list == [call(2), call(4)]
    for invocation in post.await_args_list:
        assert invocation.kwargs["headers"] == {
            "Idempotency-Key": "order_123"
        }


@pytest.mark.asyncio
async def test_capture_stops_after_three_attempts(monkeypatch):
    client = PaymentClient("test-key")
    post = AsyncMock(side_effect=[response(500), response(500), response(500)])
    sleep = AsyncMock()
    monkeypatch.setattr(client, "_post", post)
    monkeypatch.setattr("src.client.asyncio.sleep", sleep)

    try:
        with pytest.raises(CaptureError) as error:
            await client.capture("order_123", 2500)
    finally:
        await client._http.aclose()

    assert error.value.response.status_code == 500
    assert post.await_count == 3
    assert sleep.await_args_list == [call(2), call(4)]


@pytest.mark.asyncio
@pytest.mark.parametrize("status_code", [400, 401, 403, 404])
async def test_capture_does_not_retry_non_rate_limit_4xx(
    monkeypatch, status_code
):
    client = PaymentClient("test-key")
    post = AsyncMock(return_value=response(status_code))
    sleep = AsyncMock()
    monkeypatch.setattr(client, "_post", post)
    monkeypatch.setattr("src.client.asyncio.sleep", sleep)

    try:
        with pytest.raises(CaptureError) as error:
            await client.capture("order_123", 2500)
    finally:
        await client._http.aclose()

    assert error.value.response.status_code == status_code
    post.assert_awaited_once()
    sleep.assert_not_awaited()
