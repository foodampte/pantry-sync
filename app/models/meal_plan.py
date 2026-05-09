from dataclasses import dataclass, field
from datetime import date
from typing import Dict, List, Optional


@dataclass
class MealPlanItem:
    """Represents a single ingredient requirement in a meal plan."""
    ingredient_name: str
    quantity_needed: float
    unit: str

    def to_dict(self) -> dict:
        return {
            "ingredient_name": self.ingredient_name,
            "quantity_needed": self.quantity_needed,
            "unit": self.unit,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MealPlanItem":
        return cls(
            ingredient_name=data["ingredient_name"],
            quantity_needed=float(data["quantity_needed"]),
            unit=data["unit"],
        )


@dataclass
class MealPlan:
    """Represents a meal plan for a given date range."""
    name: str
    start_date: date
    end_date: date
    ingredients: List[MealPlanItem] = field(default_factory=list)
    id: Optional[str] = None

    def add_ingredient(self, item: MealPlanItem) -> None:
        """Add an ingredient requirement to this meal plan."""
        self.ingredients.append(item)

    def get_ingredient_totals(self) -> Dict[str, Dict]:
        """Aggregate total quantities needed per ingredient."""
        totals: Dict[str, Dict] = {}
        for item in self.ingredients:
            key = item.ingredient_name.lower()
            if key in totals:
                totals[key]["quantity_needed"] += item.quantity_needed
            else:
                totals[key] = {
                    "ingredient_name": item.ingredient_name,
                    "quantity_needed": item.quantity_needed,
                    "unit": item.unit,
                }
        return totals

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "ingredients": [i.to_dict() for i in self.ingredients],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MealPlan":
        plan = cls(
            name=data["name"],
            start_date=date.fromisoformat(data["start_date"]),
            end_date=date.fromisoformat(data["end_date"]),
            id=data.get("id"),
        )
        for item_data in data.get("ingredients", []):
            plan.add_ingredient(MealPlanItem.from_dict(item_data))
        return plan
