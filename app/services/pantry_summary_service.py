from typing import Dict, Any, List
from datetime import date


class PantrySummaryService:
    """Generates an overview summary of the current pantry state."""

    def __init__(self, pantry_store: dict):
        self._store = pantry_store

    def get_summary(self) -> Dict[str, Any]:
        items = list(self._store.values())
        total = len(items)

        low_stock = [i for i in items if i.is_low_stock()]
        expired = [i for i in items if i.is_expired()]
        expiring_soon = [
            i for i in items
            if not i.is_expired() and self._days_until_expiry(i) is not None
            and 0 < self._days_until_expiry(i) <= 7
        ]
        in_stock = [
            i for i in items
            if not i.is_low_stock() and not i.is_expired()
        ]

        return {
            "total_items": total,
            "in_stock_count": len(in_stock),
            "low_stock_count": len(low_stock),
            "out_of_stock_count": sum(1 for i in items if i.quantity == 0),
            "expired_count": len(expired),
            "expiring_soon_count": len(expiring_soon),
            "low_stock_items": [i.to_dict() for i in sorted(low_stock, key=lambda x: x.quantity)],
            "expired_items": [i.to_dict() for i in expired],
            "expiring_soon_items": [i.to_dict() for i in expiring_soon],
        }

    @staticmethod
    def _days_until_expiry(item) -> int | None:
        if item.expiry_date is None:
            return None
        delta = item.expiry_date - date.today()
        return delta.days
