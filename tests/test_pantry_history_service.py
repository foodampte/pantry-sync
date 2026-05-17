import pytest
from app.services.pantry_history_service import PantryHistoryService, PantryHistoryEntry


@pytest.fixture
def service():
    svc = PantryHistoryService()
    svc.record("Milk", "added", 0.0, 2.0, "litres")
    svc.record("Milk", "consumed", 2.0, 1.5, "litres")
    svc.record("Eggs", "added", 0.0, 12.0, "units")
    svc.record("Eggs", "removed", 12.0, 0.0, "units")
    return svc


def test_record_returns_entry():
    svc = PantryHistoryService()
    entry = svc.record("Flour", "added", 0.0, 500.0, "grams")
    assert isinstance(entry, PantryHistoryEntry)
    assert entry.item_name == "Flour"
    assert entry.action == "added"
    assert entry.quantity_before == 0.0
    assert entry.quantity_after == 500.0


def test_get_history_returns_all(service):
    history = service.get_history()
    assert len(history) == 4


def test_get_history_most_recent_first(service):
    history = service.get_history()
    assert history[0]["item_name"] == "Eggs"
    assert history[0]["action"] == "removed"


def test_filter_by_item_name(service):
    history = service.get_history(item_name="Milk")
    assert len(history) == 2
    assert all(e["item_name"] == "Milk" for e in history)


def test_filter_by_item_name_case_insensitive(service):
    history = service.get_history(item_name="milk")
    assert len(history) == 2


def test_filter_by_action(service):
    history = service.get_history(action="added")
    assert len(history) == 2
    assert all(e["action"] == "added" for e in history)


def test_filter_by_item_and_action(service):
    history = service.get_history(item_name="Eggs", action="removed")
    assert len(history) == 1
    assert history[0]["quantity_before"] == 12.0
    assert history[0]["quantity_after"] == 0.0


def test_to_dict_contains_expected_keys():
    svc = PantryHistoryService()
    entry = svc.record("Sugar", "updated", 100.0, 200.0, "grams")
    d = entry.to_dict()
    assert set(d.keys()) == {"item_name", "action", "quantity_before", "quantity_after", "unit", "timestamp"}


def test_clear_empties_log(service):
    service.clear()
    assert service.get_history() == []


def test_no_results_for_unknown_item(service):
    history = service.get_history(item_name="Butter")
    assert history == []
