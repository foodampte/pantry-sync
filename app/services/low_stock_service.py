from typing import List, Dict, Any
from app.models.pantry_item import PantryItem


class LowStockService:
    """Service for identifying pantry items that are low in stock."""

    def __init__(self, pantry_store: Dict[str, PantryItem]):
        self._store = pantry_store

    def get_low_stock_items(self, threshold_override: float | None = None) -> List[Dict[str, Any]]:
        """Return all pantry items that are at or below their low-stock threshold.

        Args:
            threshold_override: If provided, use this value as the low-stock
                threshold for every item instead of each item's own threshold.

        Returns:
            A list of alert dicts sorted by quantity ascending.
        """
        alerts = []
        for item in self._store.values():
            threshold = threshold_override if threshold_override is not None else item.low_stock_threshold
            if item.quantity <= threshold:
                alerts.append(self._to_alert_dict(item, threshold))

        alerts.sort(key=lambda a: a["quantity"])
        return alerts

    def get_out_of_stock_items(self) -> List[Dict[str, Any]]:
        """Return all pantry items whose quantity is zero."""
        return [
            self._to_alert_dict(item, item.low_stock_threshold)
            for item in self._store.values()
            if item.quantity == 0
        ]

    def _to_alert_dict(self, item: PantryItem, threshold: float) -> Dict[str, Any]:
        return {
            "name": item.name,
            "quantity": item.quantity,
            "unit": item.unit,
            "low_stock_threshold": threshold,
            "shortfall": max(0.0, threshold - item.quantity),
        }
