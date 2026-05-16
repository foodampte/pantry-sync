import pytest
from app.models.pantry_item import PantryItem
from app.services.low_stock_service import LowStockService


def _make_item(name: str, quantity: float, unit: str = "units", threshold: float = 2.0) -> PantryItem:
    return PantryItem(name=name, quantity=quantity, unit=unit, low_stock_threshold=threshold)


@pytest.fixture()
def store():
    items = [
        _make_item("Milk", quantity=1.0, unit="litres", threshold=2.0),
        _make_item("Eggs", quantity=6.0, unit="units", threshold=4.0),
        _make_item("Bread", quantity=0.0, unit="loaves", threshold=1.0),
        _make_item("Butter", quantity=3.0, unit="blocks", threshold=1.0),
    ]
    return {item.name: item for item in items}


@pytest.fixture()
def service(store):
    return LowStockService(store)


def test_low_stock_returns_items_at_or_below_threshold(service):
    alerts = service.get_low_stock_items()
    names = [a["name"] for a in alerts]
    assert "Milk" in names   # 1.0 <= 2.0
    assert "Bread" in names  # 0.0 <= 1.0
    assert "Eggs" not in names   # 6.0 > 4.0
    assert "Butter" not in names  # 3.0 > 1.0


def test_low_stock_sorted_by_quantity_ascending(service):
    alerts = service.get_low_stock_items()
    quantities = [a["quantity"] for a in alerts]
    assert quantities == sorted(quantities)


def test_low_stock_includes_correct_shortfall(service):
    alerts = service.get_low_stock_items()
    milk = next(a for a in alerts if a["name"] == "Milk")
    assert milk["shortfall"] == pytest.approx(1.0)  # threshold 2.0 - quantity 1.0
    bread = next(a for a in alerts if a["name"] == "Bread")
    assert bread["shortfall"] == pytest.approx(1.0)  # threshold 1.0 - quantity 0.0


def test_threshold_override_applies_to_all_items(service):
    # With override=5.0 every item except Eggs (6.0) should appear
    alerts = service.get_low_stock_items(threshold_override=5.0)
    names = [a["name"] for a in alerts]
    assert "Milk" in names
    assert "Bread" in names
    assert "Butter" in names
    assert "Eggs" not in names


def test_out_of_stock_returns_only_zero_quantity_items(service):
    out = service.get_out_of_stock_items()
    assert len(out) == 1
    assert out[0]["name"] == "Bread"


def test_empty_store_returns_no_alerts():
    svc = LowStockService({})
    assert svc.get_low_stock_items() == []
    assert svc.get_out_of_stock_items() == []


def test_alert_dict_contains_expected_keys(service):
    alerts = service.get_low_stock_items()
    for alert in alerts:
        assert {"name", "quantity", "unit", "low_stock_threshold", "shortfall"} <= alert.keys()
