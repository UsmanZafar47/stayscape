import json
from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.database import DatasetRow
from app.dataset import Catalog
from app.main import create_app
from app.schemas import ListingPage


def test_public_endpoints(client):
    assert client.get("/api/health").json() == {"status": "ok", "service": "StayScape"}
    config = client.get("/api/config")
    assert config.status_code == 200
    assert config.json()["currency"] == "USD"
    assert config.json()["currency_minor_units"] == 2
    assert config.json()["dataset"]["count"] == 300
    assert set(config.json()["property_types"]) == {"apartment", "townhouse", "house", "loft"}
    assert "database_url" not in config.text and "api_key" not in config.text
    areas = client.get("/api/areas").json()
    assert len(areas["areas"]) == 5
    assert areas["coordinate_order"] == "longitude,latitude"


def test_list_detail_and_images(client):
    response = client.get("/api/listings?limit=3")
    assert response.status_code == 200
    page = ListingPage.model_validate(response.json())
    assert page.total == 300 and len(page.items) == 3
    listing = page.items[0]
    assert client.get(f"/api/listings/{listing.id}").json() == listing.model_dump(mode="json")
    image = client.get(listing.pictures[0])
    assert image.status_code == 200 and "image/svg+xml" in image.headers["content-type"]
    assert b"SYNTHETIC" in image.content


def test_combined_api_filters(client, dataset):
    target = next(x for x in dataset.listings if x.bedrooms >= 1)
    params = [
        ("price_min_minor", target.price_minor),
        ("price_max_minor", target.price_minor),
        ("guests", target.max_guests),
        ("bedrooms", target.bedrooms),
        ("region", target.region),
        ("property_type", target.property_type.value),
        ("limit", 100),
    ] + [("amenities", a.value) for a in target.amenities]
    response = client.get("/api/listings", params=params)
    assert response.status_code == 200
    assert str(target.id) in [x["id"] for x in response.json()["items"]]
    for item in response.json()["items"]:
        assert item["price_minor"] == target.price_minor
        assert set(target.amenities) <= set(item["amenities"])
        assert item["max_guests"] >= target.max_guests
    assert client.get("/api/listings?price_max_minor=0").json()["total"] == 0


@pytest.mark.parametrize(
    "query",
    [
        "price_min_minor=500&price_max_minor=100",
        "guests=0",
        "guests=true",
        "guests=1.0",
        "price_max_minor=1.5",
        "bedrooms=-1",
        "property_type=studio",
        "amenities=teleporter",
        "limit=0",
        "limit=101",
        "offset=-1",
        "offset=1000001",
        "region=unknown",
        "price=100",
        "limit=2&limit=3",
        "amenities=wifi&amenities=wifi",
    ],
)
def test_invalid_filters_are_safe_errors(client, query):
    response = client.get("/api/listings?" + query)
    assert response.status_code == 422
    assert response.json()["error"]["code"] in ("VALIDATION_ERROR", "INVALID_REGION")
    assert "input" not in response.json()["error"]


def test_consistent_not_found_and_uuid_errors(client):
    assert client.get(f"/api/listings/{UUID(int=0)}").json()["error"]["code"] == "LISTING_NOT_FOUND"
    assert client.get("/api/listings/not-a-uuid").status_code == 422
    assert client.get("/api/missing").json()["error"]["code"] == "NOT_FOUND"
    assert client.post("/api/listings").json()["error"]["code"] == "METHOD_NOT_ALLOWED"
    assert client.post("/api/search").status_code == 422  # M4 requires a validated query body.


def test_cors(client):
    for origin, allowed in [("http://localhost:5173", True), ("https://unknown.test", False)]:
        response = client.options(
            "/api/listings", headers={"Origin": origin, "Access-Control-Request-Method": "GET"}
        )
        assert (response.headers.get("access-control-allow-origin") == origin) is allowed


def test_unseeded_database_has_safe_error(tmp_path):
    settings = Settings(_env_file=None, database_url=f"sqlite+aiosqlite:///{tmp_path}/empty.db")
    with TestClient(create_app(settings)) as client:
        response = client.get("/api/health")
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "DATABASE_UNAVAILABLE"
    assert "empty.db" not in response.text and "SELECT" not in response.text


def test_existing_data_cannot_be_relabelled_by_env(database, tmp_path):
    pricing = tmp_path / "pricing.json"
    profile = Catalog(database[1]).pricing.model_dump()
    pricing.write_text(json.dumps({"EUR": profile}))
    settings = database[1].model_copy(update={"currency_code": "EUR", "pricing_file": pricing})
    with TestClient(create_app(settings)) as client:
        for path in ["/api/health", "/api/config", "/api/areas", "/api/listings"]:
            response = client.get(path)
            assert response.status_code == 503
            assert response.json()["error"]["code"] == "DATASET_CONFIG_MISMATCH"


async def test_missing_metadata(session, database):
    row = await session.get(DatasetRow, 1)
    await session.delete(row)
    await session.commit()
    with TestClient(create_app(database[1])) as client:
        assert client.get("/api/health").json()["error"]["code"] == "DATASET_NOT_READY"


def test_repository_can_be_substituted_without_changing_routes(database, dataset):
    from app.schemas import ListingPage

    class MemoryRepository:
        async def list(self, filters, *, limit=30, offset=0):
            return ListingPage(items=[dataset.listings[0]], total=1, limit=limit, offset=offset)

        async def get(self, listing_id):
            return None

    app = create_app(database[1])
    app.dependency_overrides[app.state.repository_dependency] = lambda: MemoryRepository()
    with TestClient(app) as client:
        assert client.get("/api/listings").json()["total"] == 1
