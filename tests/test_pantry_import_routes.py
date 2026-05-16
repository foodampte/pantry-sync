import pytest
from app.main import create_app
from app.routes.pantry_routes import pantry_store


@pytest.fixture(autouse=True)
def clear_store():
    pantry_store.clear()
    yield
    pantry_store.clear()


@pytest.fixture()
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_bulk_import_creates_items(client):
    payload = [
        {"name": "rice", "quantity": 2, "unit": "kg"},
        {"name": "lentils", "quantity": 1, "unit": "kg"},
    ]
    resp = client.post("/pantry/import", json=payload)
    assert resp.status_code == 200
    data = resp.get_json()
    assert set(data["created"]) == {"rice", "lentils"}
    assert data["updated"] == []
    assert data["skipped"] == []


def test_bulk_import_updates_existing_item(client):
    client.post("/pantry/import", json=[{"name": "rice", "quantity": 1, "unit": "kg"}])
    resp = client.post("/pantry/import", json=[{"name": "rice", "quantity": 10, "unit": "kg"}])
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["updated"] == ["rice"]
    assert data["created"] == []


def test_bulk_import_returns_400_for_non_array(client):
    resp = client.post("/pantry/import", json={"name": "rice"})
    assert resp.status_code == 400
    assert "array" in resp.get_json()["error"].lower()


def test_bulk_import_reports_skipped_rows(client):
    payload = [
        {"name": "eggs", "quantity": 6, "unit": "pcs"},
        {"quantity": 3},  # no name
    ]
    resp = client.post("/pantry/import", json=payload)
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data["created"]) == 1
    assert len(data["skipped"]) == 1


def test_bulk_import_empty_array(client):
    resp = client.post("/pantry/import", json=[])
    assert resp.status_code == 200
    data = resp.get_json()
    assert data == {"created": [], "updated": [], "skipped": []}
