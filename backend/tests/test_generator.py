import json
import subprocess
import sys
from collections import Counter
from itertools import combinations

import pytest
from shapely.geometry import Point, shape

from app.config import BACKEND
from app.dataset import geojson, validate_dataset
from app.generator import GenerationError, GenerationOptions, generate
from app.geography import Geography, GeographyIndex, distance_m
from app.schemas import Vibe


def test_reproducibility_and_content(catalog, dataset):
    again = generate(catalog, GenerationOptions(count=300, seed=42))
    assert again.model_dump_json() == dataset.model_dump_json()
    other = generate(catalog, GenerationOptions(count=300, seed=43))
    assert other.model_dump_json() != dataset.model_dump_json()
    assert Counter(x.region for x in dataset.listings) == {
        r.id: 60 for r in catalog.geography.regions
    }
    assert {x.vibes[0] for x in dataset.listings} == set(Vibe)
    assert len({x.description for x in dataset.listings}) == 300
    assert len({x.title for x in dataset.listings}) == 300
    for x in dataset.listings:
        assert 2 <= len([s for s in x.description.split(".") if s.strip()]) <= 4
        assert x.max_guests <= max(2, x.bedrooms * 2 + 2)
        assert type(x.price_minor) is int
        if x.vibes[0] == Vibe.family_friendly:
            assert x.bedrooms >= 2 and x.max_guests >= 4
            assert {"crib", "washer"} <= set(x.amenities)
        if x.vibes[0] == Vibe.business:
            assert "workspace" in x.amenities
        if x.vibes[0] == Vibe.scenic:
            assert "balcony" in x.amenities


def test_all_points_spacing_and_exclusions(dataset, catalog):
    index = GeographyIndex(catalog.geography)
    for item in dataset.listings:
        assert index.allows(item.region, item.longitude, item.latitude)
    gaps = [
        distance_m((a.longitude, a.latitude), (b.longitude, b.latitude))
        for a, b in combinations(dataset.listings, 2)
    ]
    assert min(gaps) >= 75
    assert validate_dataset(dataset, catalog)["minimum_observed_spacing_m"] >= 75


def test_exclusion_boundaries_and_cross_region_exclusion(catalog):
    index = GeographyIndex(catalog.geography)
    assert not index.allows("manhattan", -73.974, 40.774)  # Central Park
    assert not index.allows("manhattan", -74.05, 40.76)  # Outside inland polygon
    for region in catalog.geography.regions:
        for zone in region.exclusions:
            p = shape({"type": "Polygon", "coordinates": [zone.polygon]}).representative_point()
            assert not index.allows(region.id, p.x, p.y)
            assert not index.allows(region.id, *zone.polygon[0])
    # A config edit moving a named exclusion across a region must not bypass global masking.
    region = catalog.geography.regions[0]
    exclusion = index.exclusions[0]
    assert exclusion.covers(Point(-73.974, 40.774))


def test_no_silent_constraint_relaxation(catalog):
    with pytest.raises(GenerationError, match="NOT relaxed"):
        generate(
            catalog,
            GenerationOptions(count=300, seed=42, min_spacing_m=100_000, attempts_per_region=100),
        )
    with pytest.raises(GenerationError, match="below"):
        generate(catalog, GenerationOptions(count=5, min_spacing_m=1))


def test_global_spacing_across_overlapping_regions(catalog):
    from copy import copy

    from app.dataset import Pricing

    custom = copy(catalog)
    a = catalog.geography.regions[0]
    b = a.model_copy(update={"id": "overlapping", "name": "Overlapping"})
    custom.geography = catalog.geography.model_copy(update={"regions": [a, b]})
    custom.pricing = Pricing(minor_units=2, region_base_minor={a.id: 20000, b.id: 20000})
    result = generate(custom, GenerationOptions(count=30, seed=12))
    for x, y in combinations(result.listings, 2):
        assert distance_m((x.longitude, x.latitude), (y.longitude, y.latitude)) >= 75


def test_corrupt_dataset_rejected_before_seed(dataset, catalog):
    items = list(dataset.listings)
    items[1] = items[1].model_copy(
        update={
            "longitude": items[0].longitude,
            "latitude": items[0].latitude,
            "region": items[0].region,
        }
    )
    with pytest.raises(ValueError, match="spacing"):
        validate_dataset(dataset.model_copy(update={"listings": items}), catalog)
    with pytest.raises(ValueError, match="configuration changed"):
        validate_dataset(dataset.model_copy(update={"regions_sha256": "0" * 64}), catalog)
    items[1] = items[1].model_copy(update={"currency": "EUR"})
    with pytest.raises(ValueError, match="currencies"):
        validate_dataset(dataset.model_copy(update={"listings": items}), catalog)


def test_config_rejects_invalid_polygon(catalog):
    data = catalog.geography.model_dump()
    data["regions"][0]["polygon"] = [[0, 0], [1, 1], [1, 0], [0, 1], [0, 0]]
    with pytest.raises(ValueError):
        Geography.model_validate(data)


def test_geojson_and_cli_failure_do_not_write_partial_output(catalog, dataset, tmp_path):
    collection = geojson(dataset, catalog.geography)
    points = [f for f in collection["features"] if f["geometry"]["type"] == "Point"]
    assert len(points) == 300
    assert points[0]["geometry"]["coordinates"] == [
        dataset.listings[0].longitude,
        dataset.listings[0].latitude,
    ]
    assert all(shape(f["geometry"]).is_valid for f in collection["features"])
    target = tmp_path / "failed.json"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "app.cli",
            "generate",
            "--count",
            "300",
            "--min-spacing-m",
            "100000",
            "--attempts-per-region",
            "100",
            "--out",
            str(target),
        ],
        cwd=BACKEND,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2
    assert "NOT relaxed" in result.stderr
    assert not target.exists()
    json.dumps(collection)  # Tuples must serialize into valid GeoJSON arrays.
