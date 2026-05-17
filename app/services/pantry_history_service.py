from datetime import datetime, timezone
from typing import Optional


class PantryHistoryEntry:
    def __init__(self, item_name: str, action: str, quantity_before: float,
                 quantity_after: float, unit: str, timestamp: Optional[datetime] = None):
        self.item_name = item_name
        self.action = action  # 'added', 'updated', 'removed', 'consumed'
        self.quantity_before = quantity_before
        self.quantity_after = quantity_after
        self.unit = unit
        self.timestamp = timestamp or datetime.now(timezone.utc)

    def to_dict(self) -> dict:
        return {
            "item_name": self.item_name,
            "action": self.action,
            "quantity_before": self.quantity_before,
            "quantity_after": self.quantity_after,
            "unit": self.unit,
            "timestamp": self.timestamp.isoformat(),
        }


class PantryHistoryService:
    def __init__(self):
        self._log: list[PantryHistoryEntry] = []

    def record(self, item_name: str, action: str, quantity_before: float,
               quantity_after: float, unit: str) -> PantryHistoryEntry:
        entry = PantryHistoryEntry(
            item_name=item_name,
            action=action,
            quantity_before=quantity_before,
            quantity_after=quantity_after,
            unit=unit,
        )
        self._log.append(entry)
        return entry

    def get_history(self, item_name: Optional[str] = None,
                    action: Optional[str] = None) -> list[dict]:
        results = self._log
        if item_name:
            results = [e for e in results if e.item_name.lower() == item_name.lower()]
        if action:
            results = [e for e in results if e.action == action]
        return [e.to_dict() for e in reversed(results)]

    def clear(self) -> None:
        self._log.clear()
