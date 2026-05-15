from datetime import date, timedelta
from typing import List, Dict, Any
from app.models.pantry_item import PantryItem


class ExpiryAlertService:
    DEFAULT_WARNING_DAYS = 7

    def __init__(self, warning_days: int = DEFAULT_WARNING_DAYS):
        self.warning_days = warning_days

    def get_alerts(self, items: List[PantryItem]) -> Dict[str, List[Dict[str, Any]]]:
        """Categorise pantry items into expired and expiring-soon buckets."""
        expired = []
        expiring_soon = []
        today = date.today()
        cutoff = today + timedelta(days=self.warning_days)

        for item in items:
            if item.expiry_date is None:
                continue
            if item.is_expired():
                expired.append(self._to_alert_dict(item, today))
            elif item.expiry_date <= cutoff:
                expiring_soon.append(self._to_alert_dict(item, today))

        return {
            "expired": expired,
            "expiring_soon": expiring_soon,
        }

    @staticmethod
    def _to_alert_dict(item: PantryItem, today: date) -> Dict[str, Any]:
        days_delta = (item.expiry_date - today).days
        return {
            "name": item.name,
            "quantity": item.quantity,
            "unit": item.unit,
            "expiry_date": item.expiry_date.isoformat(),
            "days_until_expiry": days_delta,
        }
