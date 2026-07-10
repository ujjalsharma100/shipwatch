import asyncio
import os

import httpx

from .models import CaptureResult

API_BASE_URL = os.environ.get("PROVIDER_API_URL", "https://api.provider.com")


class CaptureError(Exception):
    def __init__(self, resp: httpx.Response):
        self.response = resp
        super().__init__(f"capture failed: {resp.status_code}")


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
        resp = await self._post("/v1/captures", {"amount": amount_cents})
        if resp.status_code >= 400:
            raise CaptureError(resp)
        return CaptureResult.from_json(resp.json())

    async def _post(self, path: str, payload: dict) -> httpx.Response:
        return await self._http.post(self._base_url + path, json=payload)