import pytest
from datetime import date, timedelta
from app.models.pantry_item import PantryItem


@pytest.fixture
def basic_item():
    return PantryItem(
        name="Oats",
        quantity=500.0,
        unit="grams",
        category="grains",
        minimum_quantity=100.0,
    )


def test_pantry_item_creation(basic_item):
    assert basic_item.name == "Oats"
    assert basic_item.quantity == 500.0
    assert basic_item.unit == "grams"
    assert basic_item.category == "grains"
    assert basic_item.id is not None


def test_is_low_stock_false(basic_item):
    assert basic_item.is_low_stock() is False


def test_is_low_stock_true():
    item = PantryItem(name="Salt", quantity=50.0, unit="grams", category="condiments", minimum_quantity=100.0)
    assert item.is_low_stock() is True


def test_is_low_stock_at_threshold():
    item = PantryItem(name="Sugar", quantity=100.0, unit="grams", category="baking", minimum_quantity=100.0)
    assert item.is_low_stock() is True


def test_is_expired_no_date(basic_item):
    assert basic_item.is_expired() is False


def test_is_expired_future_date():
    item = PantryItem(
        name="Milk", quantity=1.0, unit="liters", category="dairy",
        expiry_date=date.today() + timedelta(days=5)
    )
    assert item.is_expired() is False


def test_is_expired_past_date():
    item = PantryItem(
        name="Yogurt", quantity=1.0, unit="cups", category="dairy",
        expiry_date=date.today() - timedelta(days=1)
    )
    assert item.is_expired() is True


def test_to_dict(basic_item):
    result = basic_item.to_dict()
    assert result["name"] == "Oats"
    assert result["quantity"] == 500.0
    assert result["expiry_date"] is None
    assert result["is_low_stock"] is False
    assert result["is_expired"] is False


def test_from_dict_roundtrip(basic_item):
    data = basic_item.to_dict()
    restored = PantryItem.from_dict(data)
    assert restored.name == basic_item.name
    assert restored.quantity == basic_item.quantity
    assert restored.unit == basic_item.unit
    assert restored.id == basic_item.id


def test_from_dict_with_expiry():
    data = {
        "name": "Cheese",
        "quantity": 200.0,
        "unit": "grams",
        "category": "dairy",
        "expiry_date": "2025-12-31",
    }
    item = PantryItem.from_dict(data)
    assert item.expiry_date == date(2025, 12, 31)
