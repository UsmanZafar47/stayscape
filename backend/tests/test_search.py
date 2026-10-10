import pytest
from pydantic import ValidationError

from app.search_parser import SearchIntent, parse_rules


def test_rule_parser_recognizes_supported_constraints_and_vibes():
    intent = parse_rules("Quiet family townhouse in Jersey City between $120.50 and $300 for 4 guests, 2 bedrooms with wifi and parking")
    assert intent.price_min_minor == 12050 and intent.price_max_minor == 30000
    assert (intent.guests, intent.bedrooms, intent.region, intent.property_type) == (4, 2, "jersey-city", "townhouse")
    assert set(intent.amenities) == {"wifi", "parking"}
    assert set(intent.vibes) == {"quiet", "family-friendly"}
    assert parse_rules("romantic Brooklyn loft under $250 with balcony").price_max_minor == 25000
    assert parse_rules("quiet stay without parking").amenities == []
    assert parse_rules("luxury stay with a teleporter").amenities == []


def test_search_filter_output_is_strict_and_bounded():
    for payload in ['{"guests":"2"}', '{"guests":true}', '{"bedrooms":6}',
                    '{"price_max_minor":200.5}', '{"price_min_minor":30000,"price_max_minor":10000}',
                    '{"region":"paris"}', '{"amenities":["teleporter"]}',
                    '{"vibes":["quiet","quiet"]}', '{"explanation":"invented"}']:
        with pytest.raises(ValidationError):
            SearchIntent.model_validate_json(payload)
    assert SearchIntent.model_validate_json('{"guests":2,"price_max_minor":25000}').guests == 2


def test_demo_search_is_provider_free_grounded_cached_and_rate_limited(client, monkeypatch):
    service = client.app.state.search

    async def forbidden(*args):
        raise AssertionError("Demo must not call the provider")

    monkeypatch.setattr(service.provider, "interpret", forbidden)
    query = client.get("/api/search/examples").json()["queries"][0]
    service.settings.search_rate_per_minute = 2
    response = client.post("/api/search", json={"query": query, "demo": True})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["source"] == "demo" and service.ranker is None
    assert data["items"] and len(data["items"]) <= 12
    assert "Offline demo" in data["explanation"]
    for item in data["items"]:
        assert item["price_minor"] <= 25000 and item["max_guests"] >= 2
        assert item["region"] == "manhattan" and "wifi" in item["amenities"]
    assert data["bounds"][0] == [min(x["longitude"] for x in data["items"]), min(x["latitude"] for x in data["items"])]
    assert client.post("/api/search", json={"query": query, "demo": True}).json()["cached"]
    assert client.post("/api/search", json={"query": query, "demo": True}).status_code == 429
