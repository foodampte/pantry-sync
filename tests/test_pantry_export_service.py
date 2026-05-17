import csv
import io
from datetime import date, timedelta
import pytest
from app.services.pantry_export_service import PantryExportService


def _make_item(name, quantity=5, unit="pcs", threshold=2, expiry_date=None, category=None):
    return {
        "name": name,
        "quantity": quantity,
        "unit": unit,
        "low_stock_threshold": threshold,
        "expiry_date": expiry_date,
        "category": category,
    }


@pytest.fixture
def store():
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    return {
        "milk": _make_item("milk", 2, "liters", 1, tomorrow, "dairy"),
        "eggs": _make_item("eggs", 12, "pcs", 6, yesterday, "dairy"),
        "rice": _make_item("rice", 1000, "g", 200, None, "grains"),
    }


@pytest.fixture
def service(store):
    return PantryExportService(store)


def test_export_csv_returns_string(service):
    result = service.export_csv()
    assert isinstance(result, str)


def test_export_csv_contains_header(service):
    result = service.export_csv()
    reader = csv.DictReader(io.StringIO(result))
    assert "name" in reader.fieldnames
    assert "quantity" in reader.fieldnames
    assert "expiry_date" in reader.fieldnames


def test_export_csv_includes_all_items_by_default(service):
    result = service.export_csv()
    reader = csv.DictReader(io.StringIO(result))
    names = [row["name"] for row in reader]
    assert "milk" in names
    assert "eggs" in names
    assert "rice" in names


def test_export_csv_excludes_expired_when_flag_false(service):
    result = service.export_csv(include_expired=False)
    reader = csv.DictReader(io.StringIO(result))
    names = [row["name"] for row in reader]
    assert "eggs" not in names
    assert "milk" in names
    assert "rice" in names


def test_export_csv_sorted_alphabetically(service):
    result = service.export_csv()
    reader = csv.DictReader(io.StringIO(result))
    names = [row["name"] for row in reader]
    assert names == sorted(names)


def test_export_json_returns_list(service):
    result = service.export_json()
    assert isinstance(result, list)
    assert len(result) == 3


def test_export_json_excludes_expired(service):
    result = service.export_json(include_expired=False)
    names = [item["name"] for item in result]
    assert "eggs" not in names
    assert len(result) == 2


def test_export_json_sorted_alphabetically(service):
    result = service.export_json()
    names = [item["name"] for item in result]
    assert names == sorted(names)


def test_export_empty_store():
    svc = PantryExportService({})
    csv_result = svc.export_csv()
    reader = csv.DictReader(io.StringIO(csv_result))
    assert list(reader) == []
    assert svc.export_json() == []
