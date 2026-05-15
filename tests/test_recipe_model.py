import pytest
from app.models.recipe import Recipe, RecipeIngredient


@pytest.fixture
def basic_recipe():
    r = Recipe(id="pasta", name="Pasta Bolognese", servings=2)
    r.add_ingredient("spaghetti", 200, "g")
    r.add_ingredient("ground beef", 300, "g")
    return r


def test_recipe_creation(basic_recipe):
    assert basic_recipe.id == "pasta"
    assert basic_recipe.name == "Pasta Bolognese"
    assert basic_recipe.servings == 2
    assert len(basic_recipe.ingredients) == 2


def test_add_ingredient(basic_recipe):
    basic_recipe.add_ingredient("tomato sauce", 150, "ml")
    assert len(basic_recipe.ingredients) == 3
    assert basic_recipe.ingredients[-1].name == "tomato sauce"


def test_scale_doubles_quantities(basic_recipe):
    scaled = basic_recipe.scale(4)
    assert scaled[0].quantity == 400
    assert scaled[1].quantity == 600


def test_scale_halves_quantities(basic_recipe):
    scaled = basic_recipe.scale(1)
    assert scaled[0].quantity == 100


def test_to_dict(basic_recipe):
    d = basic_recipe.to_dict()
    assert d["id"] == "pasta"
    assert d["servings"] == 2
    assert len(d["ingredients"]) == 2
    assert d["ingredients"][0]["unit"] == "g"


def test_from_dict_round_trip(basic_recipe):
    d = basic_recipe.to_dict()
    restored = Recipe.from_dict(d)
    assert restored.id == basic_recipe.id
    assert restored.name == basic_recipe.name
    assert len(restored.ingredients) == len(basic_recipe.ingredients)


def test_scale_with_zero_servings():
    r = Recipe(id="x", name="X", servings=0)
    r.add_ingredient("salt", 5, "g")
    scaled = r.scale(2)
    assert scaled[0].quantity == 5  # factor defaults to 1
