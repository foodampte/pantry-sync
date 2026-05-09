import pytest
from flask import Flask
from app.routes.pantry_routes import pantry_bp, _pantry


@pytest.fixture(autouse=True)
def clear_pantry():
    """Reset the in-memory store before every test."""
    _pantry.clear()
    yield
    _pantry.clear()


@pytest.fixture()
def client():
    app = Flask(__name__)
    app.register_blueprint(pantry_bp)
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


SAMPLE = {
    "id": "flour-001",
    "name": "All-Purpose Flour",
    "quantity": 500,
    "unit": "g",
    "low_stock_threshold": 200,
    "expiry_date": "2025-12-31",
}


def test_list_empty(client):
    resp = client.get("/pantry/")
    assert resp.status_code == 200
    assert resp.get_json() == []


def test_create_item(client):
    resp = client.post("/pantry/", json=SAMPLE)
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["id"] == SAMPLE["id"]
    assert body["name"] == SAMPLE["name"]


def test_create_duplicate_returns_409(client):
    client.post("/pantry/", json=SAMPLE)
    resp = client.post("/pantry/", json=SAMPLE)
    assert resp.status_code == 409


def test_get_item(client):
    client.post("/pantry/", json=SAMPLE)
    resp = client.get(f"/pantry/{SAMPLE['id']}")
    assert resp.status_code == 200
    assert resp.get_json()["id"] == SAMPLE["id"]


def test_get_missing_item_returns_404(client):
    resp = client.get("/pantry/does-not-exist")
    assert resp.status_code == 404


def test_update_item(client):
    client.post("/pantry/", json=SAMPLE)
    updated = {**SAMPLE, "quantity": 999}
    resp = client.put(f"/pantry/{SAMPLE['id']}", json=updated)
    assert resp.status_code == 200
    assert resp.get_json()["quantity"] == 999


def test_update_missing_item_returns_404(client):
    resp = client.put("/pantry/ghost", json=SAMPLE)
    assert resp.status_code == 404


def test_delete_item(client):
    client.post("/pantry/", json=SAMPLE)
    resp = client.delete(f"/pantry/{SAMPLE['id']}")
    assert resp.status_code == 204
    assert client.get(f"/pantry/{SAMPLE['id']}").status_code == 404


def test_low_stock_alert(client):
    low = {**SAMPLE, "quantity": 50}  # below threshold of 200
    client.post("/pantry/", json=low)
    resp = client.get("/pantry/alerts/low-stock")
    assert resp.status_code == 200
    assert len(resp.get_json()) == 1


def test_expired_alert(client):
    expired = {**SAMPLE, "id": "old-flour", "expiry_date": "2000-01-01"}
    client.post("/pantry/", json=expired)
    resp = client.get("/pantry/alerts/expired")
    assert resp.status_code == 200
    ids = [i["id"] for i in resp.get_json()]
    assert "old-flour" in ids
