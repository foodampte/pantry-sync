import pytest
from app.main import create_app
from app.routes.meal_plan_routes import _get_store


@pytest.fixture(autouse=True)
def clear_store():
    store = _get_store()
    store.clear()
    yield
    store.clear()


@pytest.fixture()
def client():
    app = create_app(testing=True)
    with app.test_client() as c:
        yield c


BASE_PLAN = {
    "plan_id": "plan-1",
    "meal_name": "Pasta Bolognese",
    "scheduled_date": "2024-08-01",
    "servings": 4,
    "ingredients": [
        {"name": "pasta", "quantity": 400, "unit": "g"},
        {"name": "ground beef", "quantity": 300, "unit": "g"},
    ],
}


def test_list_empty(client):
    resp = client.get("/meal-plans/")
    assert resp.status_code == 200
    assert resp.get_json() == []


def test_create_plan(client):
    resp = client.post("/meal-plans/", json=BASE_PLAN)
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["plan_id"] == "plan-1"
    assert body["meal_name"] == "Pasta Bolognese"
    assert len(body["ingredients"]) == 2


def test_create_duplicate_returns_409(client):
    client.post("/meal-plans/", json=BASE_PLAN)
    resp = client.post("/meal-plans/", json=BASE_PLAN)
    assert resp.status_code == 409


def test_get_plan(client):
    client.post("/meal-plans/", json=BASE_PLAN)
    resp = client.get("/meal-plans/plan-1")
    assert resp.status_code == 200
    assert resp.get_json()["meal_name"] == "Pasta Bolognese"


def test_get_missing_plan_returns_404(client):
    resp = client.get("/meal-plans/nope")
    assert resp.status_code == 404


def test_add_ingredient(client):
    client.post("/meal-plans/", json=BASE_PLAN)
    ing = {"name": "tomato sauce", "quantity": 200, "unit": "ml"}
    resp = client.post("/meal-plans/plan-1/ingredients", json=ing)
    assert resp.status_code == 200
    names = [i["name"] for i in resp.get_json()["ingredients"]]
    assert "tomato sauce" in names


def test_delete_plan(client):
    client.post("/meal-plans/", json=BASE_PLAN)
    resp = client.delete("/meal-plans/plan-1")
    assert resp.status_code == 204
    assert client.get("/meal-plans/plan-1").status_code == 404


def test_create_missing_fields_returns_400(client):
    resp = client.post("/meal-plans/", json={"plan_id": "x"})
    assert resp.status_code == 400
