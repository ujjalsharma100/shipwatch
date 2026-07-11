import asyncio
import os

import httpx

from .models import CaptureResult

API_BASE_URL = os.environ.get("PROVIDER_API_URL", "https://api.provider.com")
MAX_CAPTURE_ATTEMPTS = 3
INITIAL_CAPTURE_BACKOFF_SECONDS = 2
MAX_CAPTURE_BACKOFF_SECONDS = 10


CAPTURE_TIMEOUT_SECONDS = 15


class CaptureError(Exception):
    def __init__(
        self, resp: httpx.Response | None = None, message: str | None = None
    ):
        self.response = resp
        if message is None:
            message = f"capture failed: {resp.status_code}"
        super().__init__(message)

class CaptureRetriesExhausted(Exception):
    def __init__(self, order_id: str, amount_cents: int):
        super().__init__(
            f"capture retries exhausted for order {order_id} ({amount_cents} cents)"
        )

class PaymentClient:
    def __init__(self, api_key: str, base_url: str = API_BASE_URL):
        self._api_key = api_key
        self._base_url = base_url
        self._http = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {api_key}"}
        )

    @classmethod
    def from_env(cls) -> "PaymentClient":
        return cls(api_key=os.environ.get("PROVIDER_API_KEY", "dev-key"))

    async def capture(self, order_id: str, amount_cents: int) -> CaptureResult:
        for attempt in range(MAX_CAPTURE_ATTEMPTS):
            last_attempt = attempt == MAX_CAPTURE_ATTEMPTS - 1
            try:
                resp = await self._post(
                    "/v1/captures",
                    {"amount": amount_cents},
                    headers={"Idempotency-Key": order_id},
                )
            except CaptureError:
                # Connection failures are retryable like a 5xx response.
                if last_attempt:
                    raise
                await self._backoff(attempt)
                continue

            if resp.status_code < 400:
                return CaptureResult.from_json(resp.json())

            is_retryable = resp.status_code == 429 or resp.status_code >= 500
            if not is_retryable or last_attempt:
                raise CaptureError(resp)

            await self._backoff(attempt)

        raise CaptureRetriesExhausted(order_id, amount_cents)

    async def _backoff(self, attempt: int) -> None:
        backoff = min(
            INITIAL_CAPTURE_BACKOFF_SECONDS * (2**attempt),
            MAX_CAPTURE_BACKOFF_SECONDS,
        )
        await asyncio.sleep(backoff)

    async def _post(
        self, path: str, payload: dict, headers: dict[str, str] | None = None
    ) -> httpx.Response:
        try:
            return await self._http.post(
                self._base_url + path,
                json=payload,
                headers=headers,
                timeout=CAPTURE_TIMEOUT_SECONDS,
            )
        except httpx.TransportError as exc:
            raise CaptureError(message=f"capture request failed: {exc}") from exc