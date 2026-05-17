from datetime import date, timedelta
import pytest
from app.models.pantry_item import PantryItem
from app.services.pantry_analytics_service import PantryAnalyticsService


def _make_item(
    name,
    quantity=10,
    threshold=5,
    category=None,
    expiry_date=None,
    unit="units",
):
    return PantryItem(
        name=name,
        quantity=quantity,
        unit=unit,
        category=category,
        low_stock_threshold=threshold,
        expiry_date=expiry_date,
    )


@pytest.fixture
def mixed_store():
    today = date.today()
    return {
        "milk": _make_item("milk", quantity=2, threshold=5, category="dairy"),
        "eggs": _make_item("eggs", quantity=12, threshold=6, category="dairy"),
        "bread": _make_item("bread", quantity=1, threshold=2, category="bakery",
                            expiry_date=today + timedelta(days=3)),
        "butter": _make_item("butter", quantity=0, threshold=1, category="dairy",
                             expiry_date=today - timedelta(days=1)),
        "pasta": _make_item("pasta", quantity=5, threshold=3, category="dry goods"),
    }


@pytest.fixture
def service(mixed_store):
    return PantryAnalyticsService(mixed_store)


def test_total_items(service):
    result = service.get_analytics()
    assert result["total_items"] == 5


def test_low_stock_count(service):
    result = service.get_analytics()
    # milk (2 < 5), bread (1 < 2), butter (0 < 1)
    assert result["low_stock_count"] == 3


def test_expired_count(service):
    result = service.get_analytics()
    assert result["expired_count"] == 1


def test_expiring_soon_count(service):
    result = service.get_analytics(days_window=7)
    assert result["expiring_soon_count"] == 1


def test_expiring_soon_excludes_expired(service):
    result = service.get_analytics(days_window=7)
    names = [i["name"] for i in result["expiring_soon_items"]]
    assert "butter" not in names
    assert "bread" in names


def test_categories_counted(service):
    result = service.get_analytics()
    assert result["categories"]["dairy"] == 3
    assert result["categories"]["bakery"] == 1
    assert result["categories"]["dry goods"] == 1


def test_top_categories_sorted(service):
    result = service.get_analytics()
    top = result["top_categories"]
    assert top[0]["category"] == "dairy"
    assert top[0]["count"] == 3


def test_low_stock_items_sorted_ascending(service):
    result = service.get_analytics()
    quantities = [i["quantity"] for i in result["low_stock_items"]]
    assert quantities == sorted(quantities)


def test_empty_store():
    svc = PantryAnalyticsService({})
    result = svc.get_analytics()
    assert result["total_items"] == 0
    assert result["low_stock_count"] == 0
    assert result["categories"] == {}
