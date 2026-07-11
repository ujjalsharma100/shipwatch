import logging

from fastapi import FastAPI, Header, HTTPException, Request

from . import store
from .client import PaymentClient
from .models import OrderStatus
from .webhooks import (
    SIGNATURE_ENFORCEMENT_DATE,
    enforce_signature_verification,
    verify_signature,
)

log = logging.getLogger("shipwatch")

app = FastAPI(title="shipwatch")
client = PaymentClient.from_env()


@app.post("/webhooks/payments")
async def payment_webhook(
    request: Request, x_provider_signature: str = Header(...)
):
    raw_body = await request.body()
    if not verify_signature(raw_body, x_provider_signature):
        if enforce_signature_verification():
            raise HTTPException(status_code=401, detail="bad signature")
        log.warning(
            "webhook signature mismatch; accepting until %s",
            SIGNATURE_ENFORCEMENT_DATE.isoformat(),
        )
    event = await request.json()
    order_id = event["data"]["metadata"]["order_id"]
    if event["type"] == "payment.succeeded":
        store.set_status(order_id, OrderStatus.PAID)
    elif event["type"] == "payment.failed":
        store.set_status(order_id, OrderStatus.FAILED)
    else:
        log.info("ignoring webhook event type %s", event["type"])
    return {"ok": True}


@app.post("/orders/{order_id}/capture")
async def capture_order(order_id: str):
    order = store.get(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="unknown order")
    result = await client.capture(order.id, order.amount_cents)
    return {"capture_id": result.capture_id, "status": result.status}