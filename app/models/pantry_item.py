from dataclasses import dataclass, field
from datetime import date
from typing import Optional
import uuid


@dataclass
class PantryItem:
    """Represents a single item in the pantry inventory."""

    name: str
    quantity: float
    unit: str
    category: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    expiry_date: Optional[date] = None
    minimum_quantity: float = 0.0

    def is_low_stock(self) -> bool:
        """Returns True if quantity is at or below the minimum threshold."""
        return self.quantity <= self.minimum_quantity

    def is_expired(self) -> bool:
        """Returns True if the item has passed its expiry date."""
        if self.expiry_date is None:
            return False
        return date.today() > self.expiry_date

    def to_dict(self) -> dict:
        """Serialize the pantry item to a dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "quantity": self.quantity,
            "unit": self.unit,
            "category": self.category,
            "expiry_date": self.expiry_date.isoformat() if self.expiry_date else None,
            "minimum_quantity": self.minimum_quantity,
            "is_low_stock": self.is_low_stock(),
            "is_expired": self.is_expired(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PantryItem":
        """Deserialize a pantry item from a dictionary."""
        expiry_date = None
        if data.get("expiry_date"):
            expiry_date = date.fromisoformat(data["expiry_date"])
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            name=data["name"],
            quantity=float(data["quantity"]),
            unit=data["unit"],
            category=data["category"],
            expiry_date=expiry_date,
            minimum_quantity=float(data.get("minimum_quantity", 0.0)),
        )
