import pytest
from app.main import create_app
from app.routes.pantry_routes import _pantry_store
from app.routes.recipe_routes import _recipe_store


@pytest.fixture(autouse=True)
def clear_stores():
    _pantry_store.clear()
    _recipe_store.clear()
    yield
    _pantry_store.clear()
    _recipe_store.clear()


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def _create_pantry_item(client, name, quantity, unit="g", low_stock_threshold=10.0):
    return client.post("/pantry/", json={
        "name": name, "quantity": quantity, "unit": unit,
        "low_stock_threshold": low_stock_threshold
    })


def _create_recipe(client, name, servings=2):
    resp = client.post("/recipes/", json={"name": name, "servings": servings})
    return resp.get_json()["id"]


def _add_ingredient(client, recipe_id, name, quantity, unit):
    return client.post(f"/recipes/{recipe_id}/ingredients",
                       json={"name": name, "quantity": quantity, "unit": unit})


def test_suggest_empty_returns_empty(client):
    resp = client.get("/suggestions/")
    assert resp.status_code == 200
    assert resp.get_json() == []


def test_suggest_recipe_can_make(client):
    _create_pantry_item(client, "eggs", 6, "unit")
    _create_pantry_item(client, "cheese", 100)
    rid = _create_recipe(client, "Omelette")
    _add_ingredient(client, rid, "eggs", 3, "unit")
    _add_ingredient(client, rid, "cheese", 50, "g")

    resp = client.get("/suggestions/")
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) == 1
    assert data[0]["can_make"] is True
    assert data[0]["missing_ingredients"] == []


def test_suggest_excludes_missing_by_default(client):
    _create_pantry_item(client, "eggs", 6, "unit")
    rid = _create_recipe(client, "Omelette")
    _add_ingredient(client, rid, "eggs", 3, "unit")
    _add_ingredient(client, rid, "cheese", 50, "g")

    resp = client.get("/suggestions/?max_missing=0")
    assert resp.status_code == 200
    assert resp.get_json() == []


def test_suggest_max_missing_includes_recipe(client):
    _create_pantry_item(client, "eggs", 6, "unit")
    rid = _create_recipe(client, "Omelette")
    _add_ingredient(client, rid, "eggs", 3, "unit")
    _add_ingredient(client, rid, "cheese", 50, "g")

    resp = client.get("/suggestions/?max_missing=1")
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) == 1
    assert len(data[0]["missing_ingredients"]) == 1


def test_suggest_invalid_max_missing(client):
    resp = client.get("/suggestions/?max_missing=abc")
    assert resp.status_code == 400


def test_suggest_negative_max_missing(client):
    resp = client.get("/suggestions/?max_missing=-1")
    assert resp.status_code == 400
