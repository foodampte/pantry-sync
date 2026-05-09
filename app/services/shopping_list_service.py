from typing import Dict, List

from app.models.meal_plan import MealPlan
from app.models.pantry_item import PantryItem


class ShoppingListService:
    """Generates shopping lists by comparing meal plan needs against pantry stock."""

    def generate(self, meal_plan: MealPlan, pantry: List[PantryItem]) -> List[Dict]:
        """
        Compare meal plan ingredient requirements with current pantry inventory.

        Returns a list of items that need to be purchased, including quantities.
        Expired pantry items are treated as unavailable.
        """
        needed = meal_plan.get_ingredient_totals()
        pantry_lookup = self._build_pantry_lookup(pantry)
        shopping_list = []

        for key, requirement in needed.items():
            available = pantry_lookup.get(key, 0.0)
            shortfall = requirement["quantity_needed"] - available

            if shortfall > 0:
                shopping_list.append({
                    "ingredient_name": requirement["ingredient_name"],
                    "quantity_to_buy": round(shortfall, 2),
                    "unit": requirement["unit"],
                    "in_pantry": round(available, 2),
                    "total_needed": round(requirement["quantity_needed"], 2),
                })

        return sorted(shopping_list, key=lambda x: x["ingredient_name"].lower())

    def _build_pantry_lookup(self, pantry: List[PantryItem]) -> Dict[str, float]:
        """Build a name -> available quantity map, skipping expired items."""
        lookup: Dict[str, float] = {}
        for item in pantry:
            if item.is_expired():
                continue
            key = item.name.lower()
            lookup[key] = lookup.get(key, 0.0) + item.quantity
        return lookup
