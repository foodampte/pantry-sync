import csv
import io
from datetime import datetime
from typing import Optional


class PantryExportService:
    def __init__(self, store: dict):
        self._store = store

    def export_csv(self, include_expired: bool = True) -> str:
        """Export pantry items as a CSV string."""
        output = io.StringIO()
        fieldnames = ["name", "quantity", "unit", "low_stock_threshold", "expiry_date", "category"]
        writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()

        items = list(self._store.values())
        if not include_expired:
            today = datetime.utcnow().date()
            items = [
                item for item in items
                if not item.get("expiry_date")
                or datetime.fromisoformat(item["expiry_date"]).date() >= today
            ]

        items_sorted = sorted(items, key=lambda i: i.get("name", "").lower())
        for item in items_sorted:
            writer.writerow({
                "name": item.get("name", ""),
                "quantity": item.get("quantity", ""),
                "unit": item.get("unit", ""),
                "low_stock_threshold": item.get("low_stock_threshold", ""),
                "expiry_date": item.get("expiry_date") or "",
                "category": item.get("category") or "",
            })

        return output.getvalue()

    def export_json(self, include_expired: bool = True) -> list:
        """Export pantry items as a list of dicts."""
        items = list(self._store.values())
        if not include_expired:
            today = datetime.utcnow().date()
            items = [
                item for item in items
                if not item.get("expiry_date")
                or datetime.fromisoformat(item["expiry_date"]).date() >= today
            ]
        return sorted(items, key=lambda i: i.get("name", "").lower())
