import pytest
from app.services.pantry_import_service import PantryImportService


# ---------------------------------------------------------------------------
# fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def store():
    return {}


@pytest.fixture()
def service(store):
    return PantryImportService(store)


# ---------------------------------------------------------------------------
# tests
# ---------------------------------------------------------------------------

def test_import_creates_new_items(service, store):
    rows = [
        {"name": "rice", "quantity": 2, "unit": "kg"},
        {"name": "pasta", "quantity": 1, "unit": "kg"},
    ]
    result = service.import_items(rows)
    assert set(result["created"]) == {"rice", "pasta"}
    assert result["updated"] == []
    assert result["skipped"] == []
    assert len(store) == 2


def test_import_updates_existing_item(service, store):
    service.import_items([{"name": "rice", "quantity": 1, "unit": "kg"}])
    result = service.import_items([{"name": "rice", "quantity": 5, "unit": "kg"}])
    assert result["updated"] == ["rice"]
    assert result["created"] == []
    assert store["rice"].quantity == 5


def test_import_skips_row_without_name(service):
    result = service.import_items([{"quantity": 3, "unit": "pcs"}])
    assert len(result["skipped"]) == 1
    assert "name" in result["skipped"][0]["reason"]


def test_import_skips_non_numeric_quantity(service):
    result = service.import_items([{"name": "milk", "quantity": "lots"}])
    assert len(result["skipped"]) == 1


def test_import_skips_non_dict_row(service):
    result = service.import_items(["not-a-dict"])
    assert len(result["skipped"]) == 1


def test_import_mixed_valid_and_invalid(service, store):
    rows = [
        {"name": "eggs", "quantity": 12, "unit": "pcs"},
        {"quantity": 5},  # missing name
        {"name": "butter", "quantity": 0.5, "unit": "kg"},
    ]
    result = service.import_items(rows)
    assert len(result["created"]) == 2
    assert len(result["skipped"]) == 1
    assert len(store) == 2


def test_merge_preserves_existing_expiry_when_not_provided(service, store):
    from datetime import date
    service.import_items([{"name": "yogurt", "quantity": 3, "unit": "pcs",
                           "expiry_date": "2099-12-31"}])
    service.import_items([{"name": "yogurt", "quantity": 6}])
    assert store["yogurt"].expiry_date == date(2099, 12, 31)
    assert store["yogurt"].quantity == 6


def test_import_empty_list_returns_empty_summary(service):
    result = service.import_items([])
    assert result == {"created": [], "updated": [], "skipped": []}
