import pytest
from app.main import create_app
from app.services.recipe_service import RecipeService


@pytest.fixture(autouse=True)
def clear_store():
    svc = RecipeService()
    svc.clear()
    yield
    svc.clear()


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def _create_recipe(client, recipe_id="carbonara", name="Carbonara", servings=2):
    return client.post("/recipes/", json={"id": recipe_id, "name": name, "servings": servings})


def test_list_empty(client):
    resp = client.get("/recipes/")
    assert resp.status_code == 200
    assert resp.get_json() == []


def test_create_recipe(client):
    resp = _create_recipe(client)
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["id"] == "carbonara"
    assert data["servings"] == 2


def test_create_duplicate_returns_409(client):
    _create_recipe(client)
    resp = _create_recipe(client)
    assert resp.status_code == 409


def test_get_recipe(client):
    _create_recipe(client)
    resp = client.get("/recipes/carbonara")
    assert resp.status_code == 200
    assert resp.get_json()["name"] == "Carbonara"


def test_get_missing_recipe_returns_404(client):
    resp = client.get("/recipes/ghost")
    assert resp.status_code == 404


def test_add_ingredient(client):
    _create_recipe(client)
    resp = client.post("/recipes/carbonara/ingredients", json={"name": "eggs", "quantity": 3, "unit": "pcs"})
    assert resp.status_code == 200
    assert len(resp.get_json()["ingredients"]) == 1


def test_update_recipe(client):
    _create_recipe(client)
    resp = client.patch("/recipes/carbonara", json={"servings": 4})
    assert resp.status_code == 200
    assert resp.get_json()["servings"] == 4


def test_delete_recipe(client):
    _create_recipe(client)
    resp = client.delete("/recipes/carbonara")
    assert resp.status_code == 204
    assert client.get("/recipes/carbonara").status_code == 404
