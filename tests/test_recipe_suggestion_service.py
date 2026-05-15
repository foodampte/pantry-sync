import pytest
from app.models.recipe import Recipe, RecipeIngredient
from app.models.pantry_item import PantryItem
from app.services.recipe_suggestion_service import RecipeSuggestionService


def _make_recipe(recipe_id: str, name: str, ingredients):
    r = Recipe(id=recipe_id, name=name, servings=2)
    for ing_name, qty, unit in ingredients:
        r.add_ingredient(RecipeIngredient(name=ing_name, quantity=qty, unit=unit))
    return r


def _make_item(name: str, quantity: float, unit: str = "g"):
    return PantryItem(name=name, quantity=quantity, unit=unit, low_stock_threshold=10.0)


@pytest.fixture
def pasta_recipe():
    return _make_recipe("r1", "Pasta Bolognese", [("pasta", 200, "g"), ("mince", 300, "g"), ("tomato sauce", 150, "ml")])


@pytest.fixture
def omelette_recipe():
    return _make_recipe("r2", "Omelette", [("eggs", 3, "unit"), ("cheese", 50, "g")])


@pytest.fixture
def full_pantry():
    return {
        "pasta": _make_item("pasta", 500),
        "mince": _make_item("mince", 400),
        "tomato sauce": _make_item("tomato sauce", 200, "ml"),
        "eggs": _make_item("eggs", 6, "unit"),
        "cheese": _make_item("cheese", 100),
    }


def test_suggests_all_when_pantry_full(pasta_recipe, omelette_recipe, full_pantry):
    service = RecipeSuggestionService({"r1": pasta_recipe, "r2": omelette_recipe}, full_pantry)
    results = service.suggest()
    assert len(results) == 2
    assert all(r["can_make"] for r in results)


def test_missing_ingredient_excluded_by_default(pasta_recipe, omelette_recipe):
    pantry = {
        "pasta": _make_item("pasta", 500),
        "mince": _make_item("mince", 400),
        # tomato sauce missing
        "eggs": _make_item("eggs", 6, "unit"),
        "cheese": _make_item("cheese", 100),
    }
    service = RecipeSuggestionService({"r1": pasta_recipe, "r2": omelette_recipe}, pantry)
    results = service.suggest(max_missing=0)
    ids = [r["recipe_id"] for r in results]
    assert "r1" not in ids
    assert "r2" in ids


def test_max_missing_includes_partial_recipes(pasta_recipe, omelette_recipe):
    pantry = {
        "pasta": _make_item("pasta", 500),
        "mince": _make_item("mince", 400),
        "eggs": _make_item("eggs", 6, "unit"),
        "cheese": _make_item("cheese", 100),
    }
    service = RecipeSuggestionService({"r1": pasta_recipe, "r2": omelette_recipe}, pantry)
    results = service.suggest(max_missing=1)
    ids = [r["recipe_id"] for r in results]
    assert "r1" in ids


def test_shortfall_detected(pasta_recipe):
    pantry = {
        "pasta": _make_item("pasta", 100),   # need 200
        "mince": _make_item("mince", 400),
        "tomato sauce": _make_item("tomato sauce", 200, "ml"),
    }
    service = RecipeSuggestionService({"r1": pasta_recipe}, pantry)
    results = service.suggest()
    assert len(results) == 1
    assert results[0]["can_make"] is False
    assert results[0]["shortfall_ingredients"][0]["name"] == "pasta"


def test_empty_pantry_no_suggestions(pasta_recipe):
    service = RecipeSuggestionService({"r1": pasta_recipe}, {})
    results = service.suggest(max_missing=0)
    assert results == []


def test_sorted_by_fewest_missing(pasta_recipe, omelette_recipe):
    pantry = {
        "eggs": _make_item("eggs", 6, "unit"),
        "cheese": _make_item("cheese", 100),
    }
    service = RecipeSuggestionService({"r1": pasta_recipe, "r2": omelette_recipe}, pantry)
    results = service.suggest(max_missing=5)
    assert results[0]["recipe_id"] == "r2"
