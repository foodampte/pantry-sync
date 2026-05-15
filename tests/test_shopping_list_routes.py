import pytest
from app.main import create_app
import app.routes.pantry_routes as pantry_routes
import app.routes.meal_plan_routes as meal_plan_routes


@pytest.fixture(autouse=True)
def clear_stores():
    pantry_routes.pantry_store.clear()
    meal_plan_routes.meal_plan_store.clear()
    yield
    pantry_routes.pantry_store.clear()
    meal_plan_routes.meal_plan_store.clear()


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def _create_pantry_item(client, name, quantity, unit="units"):
    return client.post("/pantry", json={"name": name, "quantity": quantity, "unit": unit})


def _create_meal_plan(client, plan_id, name):
    return client.post("/meal-plans", json={"id": plan_id, "name": name})


def _add_ingredient(client, plan_id, ingredient, quantity, unit="units"):
    return client.post(
        f"/meal-plans/{plan_id}/ingredients",
        json={"name": ingredient, "quantity": quantity, "unit": unit},
    )


def test_generate_no_plans_returns_empty(client):
    resp = client.get("/shopping-list/generate")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["shopping_list"] == []


def test_generate_missing_items_in_shopping_list(client):
    _create_meal_plan(client, "plan1", "Week 1")
    _add_ingredient(client, "plan1", "eggs", 6)
    # No pantry items — all needed items should appear
    resp = client.get("/shopping-list/generate")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["item_count"] >= 1
    names = [item["name"] for item in data["shopping_list"]]
    assert "eggs" in names


def test_generate_sufficient_stock_excluded(client):
    _create_pantry_item(client, "milk", 4, "liters")
    _create_meal_plan(client, "plan1", "Week 1")
    _add_ingredient(client, "plan1", "milk", 2, "liters")
    resp = client.get("/shopping-list/generate")
    assert resp.status_code == 200
    data = resp.get_json()
    names = [item["name"] for item in data["shopping_list"]]
    assert "milk" not in names


def test_generate_for_specific_plan(client):
    _create_meal_plan(client, "plan1", "Week 1")
    _add_ingredient(client, "plan1", "bread", 2)
    resp = client.get("/shopping-list/generate/plan1")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["plan_id"] == "plan1"
    names = [item["name"] for item in data["shopping_list"]]
    assert "bread" in names


def test_generate_for_missing_plan_returns_404(client):
    resp = client.get("/shopping-list/generate/nonexistent")
    assert resp.status_code == 404


def test_generate_with_plan_id_filter(client):
    _create_meal_plan(client, "plan1", "Week 1")
    _create_meal_plan(client, "plan2", "Week 2")
    _add_ingredient(client, "plan1", "apples", 3)
    _add_ingredient(client, "plan2", "oranges", 5)
    resp = client.get("/shopping-list/generate?plan_id=plan1")
    assert resp.status_code == 200
    data = resp.get_json()
    names = [item["name"] for item in data["shopping_list"]]
    assert "apples" in names
    assert "oranges" not in names


def test_generate_with_invalid_plan_id_filter_returns_404(client):
    resp = client.get("/shopping-list/generate?plan_id=ghost")
    assert resp.status_code == 404
