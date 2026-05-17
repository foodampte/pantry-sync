from datetime import date, timedelta
from collections import Counter
from typing import Any


class PantryAnalyticsService:
    def __init__(self, store: dict):
        self._store = store

    def get_analytics(self, days_window: int = 30) -> dict[str, Any]:
        items = list(self._store.values())
        today = date.today()
        window_end = today + timedelta(days=days_window)

        total = len(items)
        category_counts = Counter(item.category for item in items if item.category)
        low_stock = [item for item in items if item.is_low_stock()]
        expired = [item for item in items if item.is_expired()]
        expiring_soon = [
            item for item in items
            if item.expiry_date and today < item.expiry_date <= window_end
        ]

        return {
            "total_items": total,
            "low_stock_count": len(low_stock),
            "expired_count": len(expired),
            "expiring_soon_count": len(expiring_soon),
            "expiring_soon_window_days": days_window,
            "categories": dict(category_counts),
            "top_categories": [
                {"category": cat, "count": cnt}
                for cat, cnt in category_counts.most_common(5)
            ],
            "low_stock_items": [
                {"name": i.name, "quantity": i.quantity, "unit": i.unit}
                for i in sorted(low_stock, key=lambda x: x.quantity)
            ],
            "expiring_soon_items": [
                {"name": i.name, "expiry_date": i.expiry_date.isoformat()}
                for i in sorted(expiring_soon, key=lambda x: x.expiry_date)
            ],
        }
