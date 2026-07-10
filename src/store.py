from datetime import datetime, timezone
from typing import Optional

from .models import Order, OrderStatus

_orders: dict[str, Order] = {}


def get(order_id: str) -> Optional[Order]:
    return _orders.get(order_id)


def put(order: Order) -> None:
    _orders[order.id] = order


def set_status(order_id: str, status: OrderStatus) -> None:
    order = _orders.get(order_id)
    if order is None:
        return
    order.status = status
    order.updated_at = datetime.now(timezone.utc)