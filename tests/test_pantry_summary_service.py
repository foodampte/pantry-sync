import pytest
from datetime import date, timedelta
from app.models.pantry_item import PantryItem
from app.services.pantry_summary_service import PantrySummaryService


def _make_item(name, quantity, threshold=5, expiry_date=None):
    return PantryItem(
        name=name,
        quantity=quantity,
        unit="units",
        low_stock_threshold=threshold,
        expiry_date=expiry_date,
    )


@pytest.fixture
def mixed_store():
    today = date.today()
    return {
        "flour": _make_item("flour", 10, threshold=3),
        "milk": _make_item("milk", 2, threshold=3),
        "eggs": _make_item("eggs", 0, threshold=2),
        "yogurt": _make_item("yogurt", 5, expiry_date=today - timedelta(days=1)),
        "cheese": _make_item("cheese", 8, expiry_date=today + timedelta(days=3)),
    }


@pytest.fixture
def service(mixed_store):
    return PantrySummaryService(mixed_store)


def test_total_items(service):
    summary = service.get_summary()
    assert summary["total_items"] == 5


def test_low_stock_count(service):
    summary = service.get_summary()
    # milk (2 < 3) and eggs (0 < 2)
    assert summary["low_stock_count"] == 2


def test_out_of_stock_count(service):
    summary = service.get_summary()
    assert summary["out_of_stock_count"] == 1


def test_expired_count(service):
    summary = service.get_summary()
    assert summary["expired_count"] == 1


def test_expiring_soon_count(service):
    summary = service.get_summary()
    assert summary["expiring_soon_count"] == 1


def test_low_stock_items_sorted_ascending(service):
    summary = service.get_summary()
    quantities = [i["quantity"] for i in summary["low_stock_items"]]
    assert quantities == sorted(quantities)


def test_empty_store_returns_zeros():
    svc = PantrySummaryService({})
    summary = svc.get_summary()
    assert summary["total_items"] == 0
    assert summary["low_stock_count"] == 0
    assert summary["expired_count"] == 0
    assert summary["expiring_soon_count"] == 0


def test_in_stock_count(service):
    summary = service.get_summary()
    # flour is healthy and not expired
    assert summary["in_stock_count"] >= 1
