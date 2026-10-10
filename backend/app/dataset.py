from pathlib import Path
from typing import Self

from pydantic import Field, TypeAdapter, model_validator

from app.config import BACKEND, Settings
from app.geography import Geography, GeographyIndex, distance_m, load_geography, read_json
from app.schemas import Contract, Listing, LocalImage, MinorPrice, PropertyType, Vibe


class Pricing(Contract):
    minor_units: int = Field(ge=0, le=3)
    region_base_minor: dict[str, MinorPrice]

    @model_validator(mode="after")
    def positive(self) -> Self:
        if not self.region_base_minor or any(v <= 0 for v in self.region_base_minor.values()):
            raise ValueError("Pricing baselines must be positive integer minor units")
        return self


class Catalog:
    def __init__(self, settings: Settings):
        self.geography = load_geography(settings.regions_file)
        profiles = TypeAdapter(dict[str, Pricing]).validate_python(read_json(settings.pricing_file))
        if settings.currency_code not in profiles:
            raise ValueError(
                f"No pricing profile for {settings.currency_code}; add an explicit "
                "profile and regenerate, never relabel an existing dataset"
            )
        self.currency = settings.currency_code
        self.pricing = profiles[self.currency]
        if set(self.pricing.region_base_minor) != {r.id for r in self.geography.regions}:
            raise ValueError("Pricing profile must cover exactly the configured regions")
        self.images = TypeAdapter(dict[PropertyType, list[LocalImage]]).validate_python(
            read_json(settings.images_file)
        )
        if set(self.images) != set(PropertyType) or any(not x for x in self.images.values()):
            raise ValueError("Every model property type needs local placeholders")
        for paths in self.images.values():
            for url in paths:
                if not (BACKEND / url.lstrip("/")).is_file():
                    raise ValueError(f"Missing local placeholder: {url}")
        self.corpus = TypeAdapter(dict[Vibe, list[str]]).validate_python(
            read_json(settings.corpus_file)
        )
        if set(self.corpus) != set(Vibe) or any(len(v) < 8 for v in self.corpus.values()):
            raise ValueError("Each vibe needs at least eight authored scene pairs")


class Dataset(Contract):
    schema_version: int = Field(default=2, ge=2, le=2)
    generator_version: str = "m2.1"
    seed: int = Field(strict=True)
    count: int = Field(strict=True, ge=1, le=10_000)
    currency: str = Field(pattern=r"^[A-Z]{3}$")
    minor_units: int = Field(ge=0, le=3)
    min_spacing_m: float = Field(gt=0)
    regions_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    listings: list[Listing]


def validate_dataset(dataset: Dataset, catalog: Catalog) -> dict:
    # Validate both individual records and dataset-wide invariants before any DB write.
    dataset = Dataset.model_validate_json(dataset.model_dump_json())
    if dataset.currency != catalog.currency or dataset.minor_units != catalog.pricing.minor_units:
        raise ValueError("Dataset currency does not match the configured pricing profile")
    if dataset.regions_sha256 != catalog.geography.fingerprint:
        raise ValueError("Region configuration changed; regenerate the dataset")
    if dataset.min_spacing_m < catalog.geography.min_spacing_m:
        raise ValueError("Dataset spacing cannot be below the region configuration minimum")
    if dataset.count != len(dataset.listings):
        raise ValueError("Dataset count differs from the number of listings")
    index = GeographyIndex(catalog.geography)
    seen_ids, seen_titles, seen_descriptions = set(), set(), set()
    points = []
    nearest = float("inf")
    counts = {r.id: 0 for r in catalog.geography.regions}
    for item in dataset.listings:
        if item.currency != dataset.currency:
            raise ValueError("Mixed listing currencies are not allowed")
        if (
            item.id in seen_ids
            or item.title in seen_titles
            or item.description in seen_descriptions
        ):
            raise ValueError("Duplicate listing ID, title or description")
        if not index.allows(item.region, item.longitude, item.latitude):
            raise ValueError(f"Listing {item.id} is outside its region or inside an exclusion")
        if item.pictures != catalog.images[item.property_type]:
            raise ValueError(f"Listing {item.id} has an incorrect placeholder mapping")
        sentences = [s for s in item.description.split(".") if s.strip()]
        if not 2 <= len(sentences) <= 4:
            raise ValueError("Descriptions must have two to four sentences")
        point = (item.longitude, item.latitude)
        for previous in points:
            gap = distance_m(point, previous)
            nearest = min(nearest, gap)
            if gap < dataset.min_spacing_m:
                raise ValueError(f"Global spacing violation: {gap:.2f}m < {dataset.min_spacing_m}m")
        points.append(point)
        seen_ids.add(item.id)
        seen_titles.add(item.title)
        seen_descriptions.add(item.description)
        counts[item.region] += 1
    return {
        "valid": True,
        "count": dataset.count,
        "currency": dataset.currency,
        "by_region": counts,
        "minimum_observed_spacing_m": None if nearest == float("inf") else round(nearest, 3),
        "unique_descriptions": len(seen_descriptions),
    }


def load_dataset(path: Path, catalog: Catalog) -> Dataset:
    dataset = Dataset.model_validate_json(path.read_text(encoding="utf-8-sig"))
    validate_dataset(dataset, catalog)
    return dataset


def geojson(dataset: Dataset, geography: Geography) -> dict:
    features = []
    for region in geography.regions:
        for zone, kind, color in [
            (region, "region", "#368fc2"),
            *[(e, "exclusion", "#dd493b") for e in region.exclusions],
        ]:
            features.append(
                {
                    "type": "Feature",
                    "properties": {
                        "kind": kind,
                        "region": region.id,
                        "name": zone.name,
                        "stroke": color,
                        "fill": color,
                        "fill-opacity": 0.16,
                    },
                    "geometry": {"type": "Polygon", "coordinates": [zone.polygon]},
                }
            )
    for listing in dataset.listings:
        features.append(
            {
                "type": "Feature",
                "properties": {
                    "kind": "listing",
                    "id": str(listing.id),
                    "title": listing.title,
                    "region": listing.region,
                    "property_type": listing.property_type.value,
                    "price_minor": listing.price_minor,
                    "currency": listing.currency,
                    "marker-color": "#249b73",
                    "marker-size": "small",
                },
                "geometry": {"type": "Point", "coordinates": [listing.longitude, listing.latitude]},
            }
        )
    return {"type": "FeatureCollection", "features": features}
