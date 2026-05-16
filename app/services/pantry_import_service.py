from typing import List, Dict, Any, Tuple
from app.models.pantry_item import PantryItem


class PantryImportService:
    """Bulk-import pantry items from a list of dicts, e.g. parsed from CSV/JSON."""

    def __init__(self, store: dict):
        """
        :param store: the shared in-memory pantry store  {name -> PantryItem}
        """
        self._store = store

    def import_items(
        self, rows: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Process *rows* and upsert them into the pantry store.

        Returns a summary dict with keys:
          - created  : list of item names that were newly added
          - updated  : list of item names that were merged with existing data
          - skipped  : list of {row, reason} for rows that could not be parsed
        """
        created: List[str] = []
        updated: List[str] = []
        skipped: List[Dict[str, Any]] = []

        for row in rows:
            error = self._validate_row(row)
            if error:
                skipped.append({"row": row, "reason": error})
                continue

            try:
                item = PantryItem.from_dict(row)
            except Exception as exc:  # noqa: BLE001
                skipped.append({"row": row, "reason": str(exc)})
                continue

            if item.name in self._store:
                self._merge(self._store[item.name], item)
                updated.append(item.name)
            else:
                self._store[item.name] = item
                created.append(item.name)

        return {"created": created, "updated": updated, "skipped": skipped}

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_row(row: Dict[str, Any]) -> str | None:
        if not isinstance(row, dict):
            return "row is not a dict"
        if not row.get("name"):
            return "missing required field: name"
        qty = row.get("quantity")
        if qty is not None and not isinstance(qty, (int, float)):
            return f"quantity must be numeric, got {type(qty).__name__}"
        return None

    @staticmethod
    def _merge(existing: PantryItem, incoming: PantryItem) -> None:
        """Overwrite existing item fields with non-None values from incoming."""
        if incoming.quantity is not None:
            existing.quantity = incoming.quantity
        if incoming.unit:
            existing.unit = incoming.unit
        if incoming.low_stock_threshold is not None:
            existing.low_stock_threshold = incoming.low_stock_threshold
        if incoming.expiry_date is not None:
            existing.expiry_date = incoming.expiry_date
