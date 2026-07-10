from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class OrderStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"


@dataclass
class Order:
    id: str
    amount_cents: int
    status: OrderStatus
    updated_at: datetime


@dataclass
class CaptureResult:
    capture_id: str
    order_id: str
    status: str

    @classmethod
    def from_json(cls, data: dict) -> "CaptureResult":
        return cls(
            capture_id=data["id"],
            order_id=data["metadata"]["order_id"],
            status=data["status"],
        )