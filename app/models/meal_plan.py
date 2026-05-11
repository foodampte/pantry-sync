from dataclasses import dataclass, field
from typing import List, Optional
from datetime import date


@dataclass
class MealPlanItem:
    name: str
    quantity: float
    unit: str

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "quantity": self.quantity,
            "unit": self.unit,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MealPlanItem":
        return cls(
            name=data["name"],
            quantity=float(data["quantity"]),
            unit=data["unit"],
        )


@dataclass
class MealPlan:
    plan_id: str
    meal_name: str
    scheduled_date: date
    servings: int = 1
    ingredients: List[MealPlanItem] = field(default_factory=list)

    def add_ingredient(self, item: MealPlanItem) -> None:
        self.ingredients.append(item)

    def remove_ingredient(self, name: str) -> bool:
        before = len(self.ingredients)
        self.ingredients = [i for i in self.ingredients if i.name != name]
        return len(self.ingredients) < before

    def scaled_ingredients(self, target_servings: Optional[int] = None) -> List[MealPlanItem]:
        factor = (target_servings or self.servings) / max(self.servings, 1)
        return [
            MealPlanItem(name=i.name, quantity=round(i.quantity * factor, 4), unit=i.unit)
            for i in self.ingredients
        ]

    def to_dict(self) -> dict:
        return {
            "plan_id": self.plan_id,
            "meal_name": self.meal_name,
            "scheduled_date": self.scheduled_date.isoformat(),
            "servings": self.servings,
            "ingredients": [i.to_dict() for i in self.ingredients],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MealPlan":
        plan = cls(
            plan_id=data["plan_id"],
            meal_name=data["meal_name"],
            scheduled_date=date.fromisoformat(data["scheduled_date"]),
            servings=int(data.get("servings", 1)),
        )
        for ing in data.get("ingredients", []):
            plan.add_ingredient(MealPlanItem.from_dict(ing))
        return plan
