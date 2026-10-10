import json

import pytest
from pydantic import ValidationError

from app.config import Settings
from app.dataset import Catalog, validate_dataset
from app.parsing import InvalidFilterOutput, parse_filter_output
from app.schemas import Listing, ListingFilters, PropertyType


def test_model_types_match_readonly_frontend_manifest():
    from pathlib import Path

    manifest = json.loads(
        (Path(__file__).resolve().parents[2] / "frontend/src/model-manifest.json").read_text()
    )
    assert {p.value for p in PropertyType} == {m["type"] for m in manifest}


@pytest.mark.parametrize(
    "payload",
    [
        "not json",
        "null",
        "[]",
        '{"guests":true}',
        '{"guests":"4"}',
        '{"guests":0}',
        '{"bedrooms":-1}',
        '{"price_max_minor":1.5}',
        '{"price_min_minor":500,"price_max_minor":100}',
        '{"amenities":["teleporter"]}',
        '{"sql":"DROP TABLE listings"}',
        '{"property_type":"studio"}',
        "x" * 16001,
    ],
)
def test_strict_filter_boundary(payload):
    with pytest.raises(InvalidFilterOutput):
        parse_filter_output(payload)


def test_valid_strict_filters():
    result = parse_filter_output('{"guests":4,"bedrooms":0,"price_max_minor":60000}')
    assert result == ListingFilters(guests=4, bedrooms=0, price_max_minor=60000)


@pytest.mark.parametrize(
    "change",
    [
        {"price_minor": 1.5},
        {"price_minor": True},
        {"price_minor": 0},
        {"currency": "usd"},
        {"latitude": 91},
        {"longitude": -181},
        {"latitude": float("nan")},
        {"bedrooms": 0, "max_guests": 8},
        {"property_type": "studio"},
        {"pictures": ["https://example.com/photo.jpg"]},
        {"synthetic": False},
    ],
)
def test_invalid_listing(change, dataset):
    with pytest.raises(ValidationError):
        Listing.model_validate(dataset.listings[0].model_dump() | change)


def test_currency_is_never_just_relabelled(dataset, catalog, tmp_path):
    with pytest.raises(ValueError, match="No pricing profile"):
        Catalog(Settings(_env_file=None, currency_code="EUR"))
    changed = dataset.model_copy(update={"currency": "EUR"})
    with pytest.raises(ValueError, match="currency"):
        validate_dataset(changed, catalog)


def test_explicit_alternative_profile_generates_its_own_currency(tmp_path, catalog):
    from app.generator import GenerationOptions, generate

    path = tmp_path / "pricing.json"
    path.write_text(json.dumps({"EUR": catalog.pricing.model_dump()}))
    custom = Catalog(Settings(_env_file=None, currency_code="EUR", pricing_file=path))
    result = generate(custom, GenerationOptions(count=5, seed=19))
    assert result.currency == "EUR"
    assert all(x.currency == "EUR" and type(x.price_minor) is int for x in result.listings)
    # These test profile values are invented prices, not a currency conversion.
