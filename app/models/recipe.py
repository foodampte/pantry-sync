from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class RecipeIngredient:
    name: str
    quantity: float
    unit: str

    def to_dict(self) -> dict:
        return {"name": self.name, "quantity": self.quantity, "unit": self.unit}

    @classmethod
    def from_dict(cls, data: dict) -> "RecipeIngredient":
        return cls(
            name=data["name"],
            quantity=float(data["quantity"]),
            unit=data["unit"],
        )


@dataclass
class Recipe:
    id: str
    name: str
    servings: int = 1
    ingredients: List[RecipeIngredient] = field(default_factory=list)

    def add_ingredient(self, name: str, quantity: float, unit: str) -> None:
        self.ingredients.append(RecipeIngredient(name=name, quantity=quantity, unit=unit))

    def scale(self, servings: int) -> List[RecipeIngredient]:
        """Return ingredients scaled to the requested number of servings."""
        factor = servings / self.servings if self.servings else 1
        return [
            RecipeIngredient(i.name, round(i.quantity * factor, 4), i.unit)
            for i in self.ingredients
        ]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "servings": self.servings,
            "ingredients": [i.to_dict() for i in self.ingredients],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Recipe":
        recipe = cls(
            id=data["id"],
            name=data["name"],
            servings=int(data.get("servings", 1)),
        )
        for ing in data.get("ingredients", []):
            recipe.ingredients.append(RecipeIngredient.from_dict(ing))
        return recipe
