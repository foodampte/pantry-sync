import pytest
from datetime import date, timedelta
from app.services.expiry_alert_service import ExpiryAlertService
from app.models.pantry_item import PantryItem


def _make_item(name: str, expiry_offset_days: int | None) -> PantryItem:
    expiry = None if expiry_offset_days is None else date.today() + timedelta(days=expiry_offset_days)
    return PantryItem(
        name=name,
        quantity=2,
        unit="pcs",
        low_stock_threshold=1,
        expiry_date=expiry,
    )


@pytest.fixture
def service():
    return ExpiryAlertService(warning_days=7)


def test_no_alerts_for_items_without_expiry(service):
    items = [_make_item("salt", None)]
    alerts = service.get_alerts(items)
    assert alerts["expired"] == []
    assert alerts["expiring_soon"] == []


def test_detects_expired_item(service):
    items = [_make_item("milk", -1)]
    alerts = service.get_alerts(items)
    assert len(alerts["expired"]) == 1
    assert alerts["expired"][0]["name"] == "milk"
    assert alerts["expired"][0]["days_until_expiry"] == -1


def test_detects_expiring_soon_item(service):
    items = [_make_item("yoghurt", 5)]
    alerts = service.get_alerts(items)
    assert len(alerts["expiring_soon"]) == 1
    assert alerts["expiring_soon"][0]["name"] == "yoghurt"


def test_item_outside_warning_window_not_included(service):
    items = [_make_item("cheese", 14)]
    alerts = service.get_alerts(items)
    assert alerts["expired"] == []
    assert alerts["expiring_soon"] == []


def test_item_expiring_exactly_on_cutoff_is_included(service):
    items = [_make_item("butter", 7)]
    alerts = service.get_alerts(items)
    assert len(alerts["expiring_soon"]) == 1


def test_mixed_items_categorised_correctly(service):
    items = [
        _make_item("expired_egg", -3),
        _make_item("soon_bread", 2),
        _make_item("fine_pasta", 30),
        _make_item("no_date_rice", None),
    ]
    alerts = service.get_alerts(items)
    assert len(alerts["expired"]) == 1
    assert alerts["expired"][0]["name"] == "expired_egg"
    assert len(alerts["expiring_soon"]) == 1
    assert alerts["expiring_soon"][0]["name"] == "soon_bread"


def test_custom_warning_days():
    svc = ExpiryAlertService(warning_days=30)
    items = [_make_item("olive_oil", 20)]
    alerts = svc.get_alerts(items)
    assert len(alerts["expiring_soon"]) == 1
