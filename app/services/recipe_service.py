from typing import Dict, List, Optional
from app.models.recipe import Recipe

# In-memory store — mirrors pattern used in pantry/meal-plan routes
_store: Dict[str, Recipe] = {}


class RecipeService:
    def list_recipes(self) -> List[Recipe]:
        return list(_store.values())

    def get_recipe(self, recipe_id: str) -> Optional[Recipe]:
        return _store.get(recipe_id)

    def create_recipe(self, recipe: Recipe) -> Recipe:
        if recipe.id in _store:
            raise ValueError(f"Recipe '{recipe.id}' already exists.")
        _store[recipe.id] = recipe
        return recipe

    def update_recipe(self, recipe_id: str, data: dict) -> Recipe:
        recipe = _store.get(recipe_id)
        if recipe is None:
            raise KeyError(f"Recipe '{recipe_id}' not found.")
        if "name" in data:
            recipe.name = data["name"]
        if "servings" in data:
            recipe.servings = int(data["servings"])
        return recipe

    def delete_recipe(self, recipe_id: str) -> None:
        if recipe_id not in _store:
            raise KeyError(f"Recipe '{recipe_id}' not found.")
        del _store[recipe_id]

    def add_ingredient(self, recipe_id: str, name: str, quantity: float, unit: str) -> Recipe:
        recipe = _store.get(recipe_id)
        if recipe is None:
            raise KeyError(f"Recipe '{recipe_id}' not found.")
        recipe.add_ingredient(name, quantity, unit)
        return recipe

    def clear(self) -> None:
        _store.clear()
