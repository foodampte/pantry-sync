from typing import List, Dict, Any
from app.models.recipe import Recipe
from app.models.pantry_item import PantryItem


class RecipeSuggestionService:
    """Suggests recipes based on available pantry items."""

    def __init__(self, recipe_store: Dict[str, Recipe], pantry_store: Dict[str, PantryItem]):
        self._recipes = recipe_store
        self._pantry = pantry_store

    def suggest(self, max_missing: int = 0) -> List[Dict[str, Any]]:
        """Return recipes that can be made (or nearly made) from current pantry.

        Args:
            max_missing: maximum number of ingredients allowed to be missing.
        """
        pantry_lookup = self._build_pantry_lookup()
        suggestions = []

        for recipe in self._recipes.values():
            missing, shortfall = self._analyse(recipe, pantry_lookup)
            if len(missing) <= max_missing:
                suggestions.append({
                    "recipe_id": recipe.id,
                    "name": recipe.name,
                    "missing_ingredients": missing,
                    "shortfall_ingredients": shortfall,
                    "can_make": len(missing) == 0 and len(shortfall) == 0,
                })

        suggestions.sort(key=lambda s: (len(s["missing_ingredients"]), len(s["shortfall_ingredients"])))
        return suggestions

    def _build_pantry_lookup(self) -> Dict[str, float]:
        return {
            name.lower(): item.quantity
            for name, item in self._pantry.items()
        }

    def _analyse(self, recipe: Recipe, pantry_lookup: Dict[str, float]):
        missing = []
        shortfall = []
        for ingredient in recipe.ingredients:
            key = ingredient.name.lower()
            available = pantry_lookup.get(key, 0.0)
            if available == 0.0:
                missing.append({"name": ingredient.name, "required": ingredient.quantity, "unit": ingredient.unit})
            elif available < ingredient.quantity:
                shortfall.append({
                    "name": ingredient.name,
                    "required": ingredient.quantity,
                    "available": available,
                    "unit": ingredient.unit,
                })
        return missing, shortfall
