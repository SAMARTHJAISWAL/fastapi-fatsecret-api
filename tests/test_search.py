import pytest
from fastapi.testclient import TestClient

from app import api
from app.main import app

client = TestClient(app)

APPLE = {
    "food_id": "35718",
    "food_name": "Apples",
    "food_type": "Generic",
    "food_description": "Per 100g - Calories: 52kcal",
    "food_url": "https://www.fatsecret.com/calories-nutrition/usda/apples",
}
BRANDED = {
    "food_id": "1",
    "food_name": "Apple Juice",
    "food_type": "Brand",
    "brand_name": "Acme",
    "food_description": "Per 1 cup - Calories: 110kcal",
    "food_url": "https://www.fatsecret.com/x",
}


@pytest.fixture
def fake_search(monkeypatch):
    def install(foods_payload=None, error=None):
        def fake(query, page_number=0, max_results=20):
            if error:
                raise api.FatSecretError(error)
            return foods_payload

        monkeypatch.setattr(api, "search_foods", fake)

    return install


def test_search_returns_foods(fake_search):
    fake_search({"total_results": "2", "max_results": "20", "page_number": "0", "food": [APPLE, BRANDED]})
    r = client.get("/search_foods", params={"query": "apple"})
    assert r.status_code == 200
    body = r.json()
    assert body["total_results"] == 2
    assert [f["food_id"] for f in body["foods"]] == ["35718", "1"]


def test_filter_by_food_type(fake_search):
    fake_search({"total_results": "2", "max_results": "20", "page_number": "0", "food": [APPLE, BRANDED]})
    r = client.get("/search_foods", params={"query": "apple", "food_type": "brand"})
    assert [f["food_name"] for f in r.json()["foods"]] == ["Apple Juice"]


def test_single_result_dict_is_handled(fake_search):
    fake_search({"total_results": "1", "max_results": "20", "page_number": "0", "food": APPLE})
    r = client.get("/search_foods", params={"query": "apple"})
    assert len(r.json()["foods"]) == 1


def test_no_results(fake_search):
    fake_search({"total_results": "0", "max_results": "20", "page_number": "0"})
    r = client.get("/search_foods", params={"query": "zzzz"})
    assert r.status_code == 200
    assert r.json()["foods"] == []


def test_upstream_error_maps_to_502(fake_search):
    fake_search(error="FatSecret error 21: Invalid IP address")
    r = client.get("/search_foods", params={"query": "apple"})
    assert r.status_code == 502
    assert "Invalid IP" in r.json()["detail"]


def test_max_results_validated():
    r = client.get("/search_foods", params={"query": "apple", "max_results": 100})
    assert r.status_code == 422


def test_missing_credentials(monkeypatch):
    monkeypatch.setattr(api.config, "FATSECRET_CLIENT_ID", None)
    monkeypatch.setattr(api, "_token", None)
    with pytest.raises(api.FatSecretError, match="must be set"):
        api.get_access_token()
