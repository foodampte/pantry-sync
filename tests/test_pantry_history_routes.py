import pytest
from app.main import create_app
from app.routes.pantry_history_routes import get_service


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c
    get_service().clear()


def _record(client, item_name, action, before, after, unit="units"):
    get_service().record(item_name, action, before, after, unit)


def test_list_history_empty(client):
    resp = client.get("/pantry/history")
    assert resp.status_code == 200
    assert resp.get_json() == []


def test_list_history_returns_entries(client):
    _record(client, "Milk", "added", 0.0, 2.0, "litres")
    _record(client, "Eggs", "consumed", 12.0, 10.0)
    resp = client.get("/pantry/history")
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) == 2


def test_list_history_most_recent_first(client):
    _record(client, "Milk", "added", 0.0, 2.0)
    _record(client, "Eggs", "added", 0.0, 12.0)
    data = client.get("/pantry/history").get_json()
    assert data[0]["item_name"] == "Eggs"


def test_filter_by_item_name(client):
    _record(client, "Milk", "added", 0.0, 2.0)
    _record(client, "Eggs", "added", 0.0, 12.0)
    resp = client.get("/pantry/history?item_name=Milk")
    data = resp.get_json()
    assert len(data) == 1
    assert data[0]["item_name"] == "Milk"


def test_filter_by_action(client):
    _record(client, "Milk", "added", 0.0, 2.0)
    _record(client, "Milk", "consumed", 2.0, 1.0)
    resp = client.get("/pantry/history?action=consumed")
    data = resp.get_json()
    assert len(data) == 1
    assert data[0]["action"] == "consumed"


def test_invalid_action_returns_400(client):
    resp = client.get("/pantry/history?action=stolen")
    assert resp.status_code == 400
    assert "error" in resp.get_json()


def test_item_history_endpoint(client):
    _record(client, "Flour", "added", 0.0, 500.0, "grams")
    _record(client, "Sugar", "added", 0.0, 300.0, "grams")
    resp = client.get("/pantry/history/Flour")
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) == 1
    assert data[0]["item_name"] == "Flour"


def test_item_history_endpoint_no_results(client):
    resp = client.get("/pantry/history/Butter")
    assert resp.status_code == 200
    assert resp.get_json() == []
