from datetime import date, timedelta

import pytest

from app.models.meal_plan import MealPlan, MealPlanItem
from app.models.pantry_item import PantryItem
from app.services.shopping_list_service import ShoppingListService


@pytest.fixture
def service():
    return ShoppingListService()


@pytest.fixture
def basic_meal_plan():
    plan = MealPlan(
        name="Weekly Plan",
        start_date=date.today(),
        end_date=date.today() + timedelta(days=6),
    )
    plan.add_ingredient(MealPlanItem("Milk", 2.0, "liters"))
    plan.add_ingredient(MealPlanItem("Eggs", 12.0, "units"))
    plan.add_ingredient(MealPlanItem("Flour", 500.0, "grams"))
    return plan


@pytest.fixture
def pantry():
    future = date.today() + timedelta(days=30)
    return [
        PantryItem(name="Milk", quantity=1.0, unit="liters", expiry_date=future, low_stock_threshold=0.5),
        PantryItem(name="Eggs", quantity=12.0, unit="units", expiry_date=future, low_stock_threshold=4.0),
    ]


def test_generates_shopping_list_for_missing_items(service, basic_meal_plan, pantry):
    result = service.generate(basic_meal_plan, pantry)
    names = [item["ingredient_name"] for item in result]
    assert "Flour" in names


def test_generates_shortfall_for_partial_stock(service, basic_meal_plan, pantry):
    result = service.generate(basic_meal_plan, pantry)
    milk_entry = next(i for i in result if i["ingredient_name"] == "Milk")
    assert milk_entry["quantity_to_buy"] == 1.0
    assert milk_entry["in_pantry"] == 1.0


def test_fully_stocked_item_excluded(service, basic_meal_plan, pantry):
    result = service.generate(basic_meal_plan, pantry)
    names = [item["ingredient_name"] for item in result]
    assert "Eggs" not in names


def test_expired_pantry_items_treated_as_unavailable(service, basic_meal_plan):
    past = date.today() - timedelta(days=1)
    expired_pantry = [
        PantryItem(name="Milk", quantity=5.0, unit="liters", expiry_date=past, low_stock_threshold=0.5),
    ]
    result = service.generate(basic_meal_plan, expired_pantry)
    milk_entry = next((i for i in result if i["ingredient_name"] == "Milk"), None)
    assert milk_entry is not None
    assert milk_entry["quantity_to_buy"] == 2.0


def test_empty_pantry_returns_all_ingredients(service, basic_meal_plan):
    result = service.generate(basic_meal_plan, [])
    assert len(result) == 3


def test_shopping_list_is_sorted_alphabetically(service, basic_meal_plan):
    result = service.generate(basic_meal_plan, [])
    names = [item["ingredient_name"].lower() for item in result]
    assert names == sorted(names)


def test_duplicate_ingredients_in_plan_are_aggregated(service):
    plan = MealPlan(name="Test", start_date=date.today(), end_date=date.today())
    plan.add_ingredient(MealPlanItem("Butter", 100.0, "grams"))
    plan.add_ingredient(MealPlanItem("Butter", 150.0, "grams"))
    result = service.generate(plan, [])
    assert len(result) == 1
    assert result[0]["total_needed"] == 250.0
