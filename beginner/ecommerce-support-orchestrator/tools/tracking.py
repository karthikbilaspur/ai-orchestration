"""Mock tracking system. In production, replace with a courier / order-DB API call."""
from typing import Optional
import config

MOCK_ORDERS = {
    "SHOE998": "Out for delivery",
    "SHOE101": "Delivered",
    "SHOE202": "Shipped",
    "BAG555": "Delayed",
}


def get_tracking(order_id: str) -> Optional[dict]:
    status = MOCK_ORDERS.get(order_id.upper())
    if status is None:
        return None
    return {"status": status, "link": config.TRACKING_URL.format(order_id=order_id.upper())}
