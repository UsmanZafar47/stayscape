# M2 full source

Complete application, configuration, local placeholders and tests. The working files are authoritative. Exact third-party dependency pins/hashes are stored separately in backend/uv.lock and backend/requirements.lock; generated datasets and databases are reproducible outputs. Frontend source is unchanged.

## backend/.env.example

```text

# Run the backend independently; no frontend environment changes are required.
APP_NAME=StayScape
CURRENCY_CODE=USD
CORS_ORIGINS=["http://localhost:5173","http://127.0.0.1:5173"]
# When omitted, SQLite is resolved absolutely to backend/data/stayscape-m2.db.
# DATABASE_URL=sqlite+aiosqlite:///./data/stayscape-m2.db
# Optional Postgres target (asyncpg is installed). Supply your own credentials:
# DATABASE_URL=postgresql+asyncpg://USER:PASSWORD@localhost:5432/stayscape
# Optional absolute paths for custom regions and explicit currency pricing profiles:
# REGIONS_FILE=C:/path/to/regions.json
# PRICING_FILE=C:/path/to/pricing.json


```

## backend/.python-version

```text

3.12


```

## backend/pyproject.toml

```toml

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "stayscape-backend"
version = "0.2.0"
description = "Synthetic rental explorer API"
requires-python = ">=3.11"
dependencies = [
  "fastapi>=0.115,<1",
  "pydantic>=2.10,<3",
  "pydantic-settings>=2.7,<3",
  "uvicorn>=0.34,<1",
  "sqlalchemy[asyncio]>=2.0.36,<2.1",
  "aiosqlite>=0.20,<1",
  "asyncpg>=0.30,<1",
  "shapely>=2.0,<3",
]

[project.optional-dependencies]
dev = ["pytest>=8,<10", "pytest-asyncio>=0.25,<2", "httpx>=0.28,<1", "ruff>=0.9,<1"]

[dependency-groups]
dev = ["pytest>=8,<10", "pytest-asyncio>=0.25,<2", "httpx>=0.28,<1", "ruff>=0.9,<1"]

[tool.hatch.build.targets.wheel]
packages = ["app"]

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"

[tool.ruff]
target-version = "py311"
line-length = 100
extend-exclude = [".python", ".uv-cache", ".venv"]

[tool.ruff.lint]
select = ["E", "F", "I"]


```

## backend/app/__init__.py

```python

"""StayScape backend."""


```

## backend/app/cli.py

```python

import argparse
import asyncio
import json
import sys
from pathlib import Path

from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.config import BACKEND, Settings
from app.database import make_engine
from app.dataset import Catalog, geojson, load_dataset, validate_dataset
from app.generator import GenerationOptions, generate
from app.seeding import seed_database


def write_json(path: Path, value: dict, *, overwrite: bool) -> None:
    if path.exists() and not overwrite:
        raise ValueError(f"Output already exists: {path}; use --overwrite explicitly")
    path.parent.mkdir(parents=True, exist_ok=True)
    # Build/validate first, then atomically replace the output. Failed generation writes nothing.
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    temporary.replace(path)


async def seed(settings, dataset, catalog, replace):
    engine = make_engine(settings.database_url)
    try:
        await seed_database(engine, dataset, catalog, replace=replace)
    finally:
        await engine.dispose()


def main() -> int:
    parser = argparse.ArgumentParser(description="StayScape offline M2 dataset tools")
    commands = parser.add_subparsers(dest="command", required=True)
    generation = commands.add_parser("generate")
    generation.add_argument("--count", type=int, default=300)
    generation.add_argument("--seed", type=int, default=42)
    generation.add_argument("--min-spacing-m", type=float)
    generation.add_argument("--attempts-per-region", type=int, default=30_000)
    generation.add_argument("--out", type=Path, default=BACKEND / "data/listings.json")
    generation.add_argument("--overwrite", action="store_true")
    for name in ("validate", "seed", "export-geojson"):
        command = commands.add_parser(name)
        command.add_argument("--input", type=Path, default=BACKEND / "data/listings.json")
        if name == "seed":
            command.add_argument("--replace", action="store_true")
        if name == "export-geojson":
            command.add_argument("--out", type=Path, default=BACKEND / "data/listings.geojson")
            command.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    try:
        settings = Settings()
        catalog = Catalog(settings)
        if args.command == "generate":
            dataset = generate(
                catalog,
                GenerationOptions(
                    count=args.count,
                    seed=args.seed,
                    min_spacing_m=args.min_spacing_m,
                    attempts_per_region=args.attempts_per_region,
                ),
            )
            write_json(args.out, dataset.model_dump(mode="json"), overwrite=args.overwrite)
            print(json.dumps(validate_dataset(dataset, catalog), indent=2))
        else:
            dataset = load_dataset(args.input, catalog)
            if args.command == "validate":
                print(json.dumps(validate_dataset(dataset, catalog), indent=2))
            elif args.command == "seed":
                asyncio.run(seed(settings, dataset, catalog, args.replace))
                print(f"Seeded {dataset.count} synthetic {dataset.currency} listings.")
            else:
                write_json(args.out, geojson(dataset, catalog.geography), overwrite=args.overwrite)
                print(f"Exported {dataset.count} points, regions and exclusions to {args.out}")
        return 0
    except ValidationError as exc:
        print(
            f"VALIDATION_ERROR: {exc.error_count()} invalid field(s); check input/configuration.",
            file=sys.stderr,
        )
    except SQLAlchemyError:
        print(
            "DATABASE_ERROR: seed failed; check the configured database and schema.",
            file=sys.stderr,
        )
    except (ValueError, OSError) as exc:
        print(f"DATASET_ERROR: {exc}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())


```

## backend/app/config.py

```python

from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    # Backend-local settings avoid inheriting the superseded root M1 AI settings.
    model_config = SettingsConfigDict(env_file=BACKEND / ".env", extra="ignore")

    app_name: str = "StayScape"
    database_url: str = f"sqlite+aiosqlite:///{(BACKEND / 'data/stayscape-m2.db').as_posix()}"
    currency_code: str = Field(default="USD", pattern=r"^[A-Z]{3}$")
    regions_file: Path = BACKEND / "config/regions.json"
    pricing_file: Path = BACKEND / "config/pricing.json"
    images_file: Path = BACKEND / "config/images.json"
    corpus_file: Path = BACKEND / "config/descriptions.json"
    cors_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:5173", "http://127.0.0.1:5173"]
    )

    @field_validator("database_url")
    @classmethod
    def async_driver_only(cls, value: str) -> str:
        if not value.startswith(("sqlite+aiosqlite:///", "postgresql+asyncpg://")):
            raise ValueError("Use sqlite+aiosqlite or postgresql+asyncpg")
        return value


```

## backend/app/database.py

```python

from pathlib import Path
from uuid import UUID

from sqlalchemy import JSON, CheckConstraint, Float, ForeignKey, Integer, String, Uuid, event
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class ListingRow(Base):
    __tablename__ = "listings"
    __table_args__ = (
        CheckConstraint("price_minor > 0 AND price_minor <= 10000000", name="ck_price"),
        CheckConstraint("rating >= 3.5 AND rating <= 5", name="ck_rating"),
        CheckConstraint("bedrooms >= 0 AND bedrooms <= 5", name="ck_bedrooms"),
        CheckConstraint("max_guests >= 1 AND max_guests <= 10", name="ck_guests"),
        CheckConstraint("max_guests <= bedrooms * 2 + 2", name="ck_capacity"),
        CheckConstraint(
            "property_type IN ('apartment','townhouse','house','loft')", name="ck_type"
        ),
        CheckConstraint(
            "property_type NOT IN ('house','townhouse') OR bedrooms >= 1", name="ck_house_bedrooms"
        ),
        CheckConstraint(
            "latitude BETWEEN -90 AND 90 AND longitude BETWEEN -180 AND 180", name="ck_coordinates"
        ),
        CheckConstraint("length(currency) = 3 AND currency = upper(currency)", name="ck_currency"),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    title: Mapped[str] = mapped_column(String(120))
    pictures: Mapped[list] = mapped_column(JSON)
    description: Mapped[str] = mapped_column(String(3000))
    price_minor: Mapped[int] = mapped_column(Integer, index=True)
    currency: Mapped[str] = mapped_column(String(3))
    rating: Mapped[float] = mapped_column(Float)
    bedrooms: Mapped[int] = mapped_column(Integer)
    max_guests: Mapped[int] = mapped_column(Integer)
    property_type: Mapped[str] = mapped_column(String(20), index=True)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    neighborhood: Mapped[str] = mapped_column(String(80))
    region: Mapped[str] = mapped_column(String(80), index=True)
    vibes: Mapped[list] = mapped_column(JSON)
    # Normalize searchable amenities: portable EXISTS queries work in SQLite and Postgres.
    # JSON is reserved for fields we do not filter in M2.
    amenity_rows: Mapped[list["AmenityRow"]] = relationship(
        cascade="all, delete-orphan", lazy="raise"
    )


class AmenityRow(Base):
    __tablename__ = "listing_amenities"
    listing_id: Mapped[UUID] = mapped_column(
        ForeignKey("listings.id", ondelete="CASCADE"), primary_key=True
    )
    amenity: Mapped[str] = mapped_column(String(30), primary_key=True)


class DatasetRow(Base):
    __tablename__ = "dataset_metadata"
    __table_args__ = (CheckConstraint("id = 1", name="ck_single_dataset"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    manifest: Mapped[dict] = mapped_column(JSON)


def make_engine(url: str) -> AsyncEngine:
    parsed = make_url(url)
    sqlite = parsed.get_backend_name() == "sqlite"
    if sqlite and parsed.database and parsed.database != ":memory:":
        Path(parsed.database).parent.mkdir(parents=True, exist_ok=True)
    engine = create_async_engine(
        url, pool_pre_ping=True, connect_args={"timeout": 15} if sqlite else {}
    )
    if sqlite:

        @event.listens_for(engine.sync_engine, "connect")
        def foreign_keys(connection, _):
            cursor = connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return engine


def session_factory(engine: AsyncEngine):
    # One session per request: AsyncSession must not be shared across concurrent requests.
    return async_sessionmaker(engine, expire_on_commit=False)


```

## backend/app/dataset.py

```python

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


```

## backend/app/errors.py

```python

class ServiceError(Exception):
    def __init__(self, code: str, message: str, status: int = 503):
        self.code = code
        self.message = message
        self.status = status
        super().__init__(message)


```

## backend/app/generator.py

```python

import random
from uuid import NAMESPACE_URL, uuid5

from pydantic import Field

from app.dataset import Catalog, Dataset, validate_dataset
from app.geography import GeographyIndex, distance_m
from app.schemas import Amenity, Contract, Listing, PropertyType, Vibe


class GenerationError(ValueError):
    pass


class GenerationOptions(Contract):
    count: int = Field(default=300, strict=True, ge=1, le=10_000)
    seed: int = Field(default=42, strict=True)
    min_spacing_m: float | None = Field(default=None, gt=0, le=100_000)
    attempts_per_region: int = Field(default=30_000, strict=True, ge=1, le=1_000_000)


TITLE_WORDS = {
    Vibe.quiet: ["Reading room", "Slow morning", "Quiet corner", "Tea and pages"],
    Vibe.nightlife: ["After hours", "Evening lights", "City rhythm", "Late breakfast"],
    Vibe.family_friendly: ["Shared table", "Family days", "Home together", "Little explorers"],
    Vibe.romantic: ["Lamplight", "Two chairs", "Soft evening", "Coffee for two"],
    Vibe.business: ["Work and unwind", "City assignment", "Desk and daylight", "Weekday retreat"],
    Vibe.budget: ["Simple comforts", "Everyday escape", "Smart city base", "Less fuss"],
    Vibe.luxury: ["Considered comfort", "Velvet evening", "The curated stay", "Special occasion"],
    Vibe.scenic: ["Sky and rooftops", "Open outlook", "Balcony journal", "Changing light"],
}
ROOM_DETAILS = {
    PropertyType.apartment: [
        "The apartment keeps its cooking and sitting areas close together for easy everyday use.",
        "A compact entry leads into the apartment's main living space without wasted corridors.",
        "This apartment makes useful room for unpacking with shelves beside the sitting area.",
        "The apartment's dining corner is deliberately small enough to leave the lounge open.",
    ],
    PropertyType.townhouse: [
        "The townhouse has an internal staircase, so it is not a step-free stay.",
        "A narrow staircase links the townhouse's living and sleeping spaces.",
        "The townhouse layout separates the upstairs sleeping area from daily activity below.",
        "This townhouse trades a wide floor plan for rooms arranged across separate levels.",
    ],
    PropertyType.house: [
        "The house has a distinct living room where guests can gather between outings.",
        "A practical entry area gives the house a comfortable place to leave coats and bags.",
        "Separate sleeping rooms make this house useful for guests keeping different routines.",
        "The house's shared dining space provides a natural meeting point throughout the day.",
    ],
    PropertyType.loft: [
        "The loft keeps a broad central living area instead of dividing it "
        "into several small rooms.",
        "An open-plan lounge gives this loft an airy character, with a clearly "
        "defined dining corner.",
        "The loft's industrial-inspired shelving adds character without filling "
        "the open floor space.",
        "Tall shelving and an open gathering area give the loft its distinctive proportions.",
    ],
}


def capacity_sentence(bedrooms: int, guests: int, rng: random.Random) -> str:
    room = (
        "an open-plan sleeping area"
        if bedrooms == 0
        else ("one separate bedroom" if bedrooms == 1 else f"{bedrooms} separate bedrooms")
    )
    sofa = " including a sofa bed" if guests > max(2, bedrooms * 2) else ""
    return rng.choice(
        [
            f"The stay has {room} and accommodates up to {guests} guests{sofa}.",
            f"Sleeping arrangements use {room}, with space for up to {guests} guests{sofa}.",
            f"Up to {guests} guests can stay here{sofa}, using {room}.",
            f"With {room}, the home welcomes a maximum of {guests} guests{sofa}.",
        ]
    )


def generate(catalog: Catalog, options: GenerationOptions) -> Dataset:
    # Local RNGs leave global randomness untouched. Content edits cannot move map points.
    rng = random.Random(options.seed)
    text_rng = random.Random(f"content:{options.seed}")
    geography = catalog.geography
    spacing = options.min_spacing_m or geography.min_spacing_m
    if spacing < geography.min_spacing_m:
        raise GenerationError("Requested spacing is below the configured minimum")
    index = GeographyIndex(geography)
    accepted = []
    # Equal regional quotas ensure a demo covers all five regions instead of favoring area size.
    # Each region checks against ALL earlier points, including points in other regions.
    for number, region in enumerate(geography.regions):
        target = options.count // len(geography.regions) + (
            number < options.count % len(geography.regions)
        )
        west, south, east, north = index.regions[region.id].bounds
        placed = 0
        for _ in range(options.attempts_per_region):
            if placed == target:
                break
            point = (round(rng.uniform(west, east), 7), round(rng.uniform(south, north), 7))
            if not index.allows(region.id, *point):
                continue
            if any(distance_m(point, previous[1]) < spacing for previous in accepted):
                continue
            accepted.append((region, point))
            placed += 1
        if placed != target:
            raise GenerationError(
                f"Could place only {placed}/{target} in {region.id} "
                f"({len(accepted)}/{options.count} globally) at {spacing:g}m spacing after "
                f"{options.attempts_per_region} attempts. Constraints were NOT relaxed. "
                "Reduce count, review/expand allowed polygons, or increase the attempt budget. "
                "Rejection sampling exhaustion does not prove mathematical infeasibility."
            )

    listings, titles, descriptions = [], set(), set()
    for i, (region, (lon, lat)) in enumerate(accepted):
        vibe = list(Vibe)[(i + options.seed) % len(Vibe)]
        # Houses are uncommon in the Manhattan sample; this remains a fictional rental catalog.
        weights = [60, 18, 2, 20] if region.id == "manhattan" else [45, 22, 16, 17]
        kind = text_rng.choices(list(PropertyType), weights=weights)[0]
        bedrooms = text_rng.choice(
            {
                PropertyType.apartment: [0, 1, 1, 2],
                PropertyType.loft: [0, 1, 1, 2],
                PropertyType.townhouse: [1, 2, 2, 3],
                PropertyType.house: [2, 2, 3, 4],
            }[kind]
        )
        if vibe == Vibe.family_friendly:
            bedrooms = max(2, bedrooms)
        if vibe == Vibe.romantic:
            bedrooms = max(1, bedrooms)
        guests = text_rng.randint(max(1, bedrooms), min(10, max(2, bedrooms * 2 + 2)))
        if bedrooms == 0:
            guests = 2
        if vibe == Vibe.family_friendly:
            guests = max(4, guests)
        if vibe == Vibe.romantic:
            guests = 2
        amenities = {Amenity.wifi, Amenity.kitchen, Amenity.air_conditioning}
        if vibe == Vibe.business:
            amenities.add(Amenity.workspace)
        if vibe == Vibe.family_friendly:
            amenities.update([Amenity.crib, Amenity.washer])
        if vibe in (Vibe.scenic, Vibe.luxury):
            amenities.add(Amenity.balcony)
        if vibe == Vibe.luxury:
            amenities.update([Amenity.washer, Amenity.workspace])
        if vibe != Vibe.budget:
            for amenity in (Amenity.washer, Amenity.pet_friendly, Amenity.workspace):
                if text_rng.random() < 0.35:
                    amenities.add(amenity)
        if kind == PropertyType.house and region.id != "manhattan" and text_rng.random() < 0.6:
            amenities.add(Amenity.parking)
        if kind == PropertyType.apartment and text_rng.random() < 0.6:
            amenities.add(Amenity.elevator)
        base = catalog.pricing.region_base_minor[region.id]
        type_factor = {
            PropertyType.apartment: 1,
            PropertyType.loft: 1.15,
            PropertyType.townhouse: 1.25,
            PropertyType.house: 1.35,
        }[kind]
        vibe_factor = {Vibe.budget: 0.62, Vibe.luxury: 1.8, Vibe.scenic: 1.12}.get(vibe, 1)
        # Integer arithmetic at storage boundaries; no floating money reaches the API or DB.
        nightly = round(
            base
            * type_factor
            * (1 + 0.22 * (bedrooms - 1))
            * vibe_factor
            * text_rng.uniform(0.84, 1.16)
        )
        unit = 10**catalog.pricing.minor_units
        nightly = max(unit, round(nightly / unit) * unit)
        for _ in range(500):
            title = (
                f"{text_rng.choice(TITLE_WORDS[vibe])}: "
                f"{text_rng.choice(['Juniper', 'Cedar', 'Willow', 'Maple', 'Amber', 'Olive'])} "
                f"{kind.value} in {region.name}"
            )
            scene = text_rng.choice(catalog.corpus[vibe])
            facts = capacity_sentence(bedrooms, guests, text_rng)
            layout = text_rng.choice(ROOM_DETAILS[kind])
            # Whole authored scene pairs preserve a coherent voice. Four possible sentence
            # orders avoid one repeated opening while capacity/layout stay grounded in fields.
            parts = text_rng.choice(
                [
                    [scene, facts, layout],
                    [layout, scene, facts],
                    [facts, scene, layout],
                    [scene, layout, facts],
                ]
            )
            description = " ".join(parts)
            if title not in titles and description not in descriptions:
                break
        else:
            raise GenerationError("Authored content combinations exhausted; expand the corpus")
        listing = Listing(
            id=uuid5(NAMESPACE_URL, f"stayscape:m2:{options.seed}:{i}:{region.id}:{lon}:{lat}"),
            title=title,
            pictures=catalog.images[kind],
            description=description,
            price_minor=nightly,
            currency=catalog.currency,
            rating=round(3.5 + 1.5 * text_rng.betavariate(9, 2), 2),
            bedrooms=bedrooms,
            max_guests=guests,
            amenities=sorted(amenities),
            property_type=kind,
            latitude=lat,
            longitude=lon,
            neighborhood=region.neighborhood,
            region=region.id,
            vibes=[vibe],
        )
        listings.append(listing)
        titles.add(title)
        descriptions.add(description)
    dataset = Dataset(
        seed=options.seed,
        count=options.count,
        currency=catalog.currency,
        minor_units=catalog.pricing.minor_units,
        min_spacing_m=spacing,
        regions_sha256=geography.fingerprint,
        listings=listings,
    )
    validate_dataset(dataset, catalog)
    return dataset


```

## backend/app/geography.py

```python

import hashlib
import json
from math import asin, cos, radians, sin, sqrt
from pathlib import Path
from typing import Annotated, Self

from pydantic import Field, model_validator
from shapely.geometry import Point, Polygon

from app.schemas import Contract

Coordinate = tuple[Annotated[float, Field(ge=-180, le=180)], Annotated[float, Field(ge=-90, le=90)]]


class Zone(Contract):
    name: str
    polygon: list[Coordinate] = Field(min_length=4)

    @model_validator(mode="after")
    def valid_ring(self) -> Self:
        shape = Polygon(self.polygon)
        if self.polygon[0] != self.polygon[-1] or not shape.is_valid or shape.area <= 0:
            raise ValueError("Polygon must be closed, nonempty and non-self-intersecting")
        return self


class Region(Zone):
    id: str = Field(pattern=r"^[a-z]+(?:-[a-z]+)*$")
    neighborhood: str
    center: Coordinate
    exclusions: list[Zone]


class Geography(Contract):
    version: int
    coordinate_order: str
    min_spacing_m: float = Field(gt=0, le=100_000)
    notes: str
    regions: list[Region] = Field(min_length=1)

    @model_validator(mode="after")
    def unique_regions(self) -> Self:
        if len({r.id for r in self.regions}) != len(self.regions):
            raise ValueError("Region IDs must be unique")
        if self.coordinate_order != "longitude,latitude":
            raise ValueError("GeoJSON coordinates must be longitude,latitude")
        for region in self.regions:
            if not Polygon(region.polygon).contains(Point(region.center)):
                raise ValueError(f"Center must be inside {region.id}")
        return self

    @property
    def fingerprint(self) -> str:
        return hashlib.sha256(self.model_dump_json().encode()).hexdigest()


def load_geography(path: Path) -> Geography:
    return Geography.model_validate_json(path.read_text(encoding="utf-8-sig"))


class GeographyIndex:
    def __init__(self, geography: Geography):
        self.regions = {r.id: Polygon(r.polygon) for r in geography.regions}
        # Apply every exclusion globally, even if a future config overlaps two regions.
        self.exclusions = [Polygon(e.polygon) for r in geography.regions for e in r.exclusions]

    def allows(self, region: str, lon: float, lat: float) -> bool:
        point = Point(lon, lat)
        # Boundaries are rejected: points on a park edge are not safely outside it.
        return (
            region in self.regions
            and self.regions[region].contains(point)
            and not any(p.covers(point) for p in self.exclusions)
        )


def distance_m(a: Coordinate, b: Coordinate) -> float:
    # Haversine avoids mistaking longitude degrees for meters at NYC's latitude.
    lon1, lat1, lon2, lat2 = map(radians, (*a, *b))
    h = sin((lat2 - lat1) / 2) ** 2 + cos(lat1) * cos(lat2) * sin((lon2 - lon1) / 2) ** 2
    return 2 * 6_371_008.8 * asin(sqrt(min(1, h)))


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


```

## backend/app/main.py

```python

import logging
from contextlib import asynccontextmanager
from typing import Annotated
from uuid import UUID

from fastapi import Depends, FastAPI, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException

from app.config import BACKEND, Settings
from app.database import make_engine, session_factory
from app.dataset import Catalog
from app.errors import ServiceError
from app.repository import ListingRepository
from app.schemas import (
    Amenity,
    HealthResponse,
    Listing,
    ListingFilters,
    ListingPage,
    ListingQuery,
    PropertyType,
)
from app.seeding import check_dataset
from app.sql_repository import SQLListingRepository

logger = logging.getLogger(__name__)


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings if settings is not None else Settings()
    catalog = Catalog(settings)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        engine = make_engine(settings.database_url)
        app.state.sessions = session_factory(engine)
        try:
            yield
        finally:
            await engine.dispose()

    app = FastAPI(title=settings.app_name, version="0.2.0", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=False,
        allow_methods=["GET"],
        allow_headers=["Content-Type"],
    )
    app.mount("/static", StaticFiles(directory=BACKEND / "static"), name="static")

    def failure(status: int, code: str, message: str, fields: list | None = None):
        body = {"code": code, "message": message}
        if fields:
            body["fields"] = fields
        return JSONResponse(status_code=status, content={"error": body})

    @app.exception_handler(ServiceError)
    async def service_error(_request, exc):
        return failure(exc.status, exc.code, exc.message)

    @app.exception_handler(RequestValidationError)
    async def invalid_request(_request, exc):
        # Never echo Pydantic's raw input, exception context, SQL, or connection strings.
        allowed = set(ListingQuery.model_fields) | {"listing_id"}
        fields = sorted(
            {str(e["loc"][-1]) if str(e["loc"][-1]) in allowed else "query" for e in exc.errors()}
        )
        return failure(
            422, "VALIDATION_ERROR", "One or more request parameters are invalid.", fields
        )

    @app.exception_handler(HTTPException)
    async def http_error(_request, exc):
        return failure(
            exc.status_code,
            {404: "NOT_FOUND", 405: "METHOD_NOT_ALLOWED"}.get(exc.status_code, "REQUEST_ERROR"),
            {
                404: "The requested resource was not found.",
                405: "This HTTP method is not supported.",
            }.get(exc.status_code, "The request could not be completed."),
        )

    @app.exception_handler(SQLAlchemyError)
    async def database_error(_request, _exc):
        logger.error("Database operation failed")  # Deliberately omit SQL/bind parameters.
        return failure(
            503, "DATABASE_UNAVAILABLE", "The database is unavailable. Check setup and retry."
        )

    @app.exception_handler(Exception)
    async def internal_error(_request, _exc):
        logger.error("Unexpected API failure")
        return failure(500, "INTERNAL_ERROR", "The request could not be completed.")

    async def session_dependency(request: Request):
        async with request.app.state.sessions() as session:
            # Readiness includes dataset/config compatibility, not just a successful connection.
            await check_dataset(session, catalog)
            yield session

    async def repository(session=Depends(session_dependency)) -> ListingRepository:
        return SQLListingRepository(session)

    # Expose the dependency callable for explicit repository substitution in tests/integrations.
    app.state.repository_dependency = repository

    @app.get("/api/health", response_model=HealthResponse)
    async def health(session=Depends(session_dependency)):
        return HealthResponse(service=settings.app_name)

    @app.get("/api/config")
    async def config(session=Depends(session_dependency)):
        manifest = await check_dataset(session, catalog)
        return {
            "currency": catalog.currency,
            "currency_minor_units": catalog.pricing.minor_units,
            "property_types": [p.value for p in PropertyType],
            "amenities": [a.value for a in Amenity],
            "pagination": {"default_limit": 30, "max_limit": 100},
            "dataset": manifest,
            "synthetic": True,
        }

    @app.get("/api/areas")
    async def areas(session=Depends(session_dependency)):
        return {
            "areas": [r.model_dump() for r in catalog.geography.regions],
            "coordinate_order": "longitude,latitude",
            "minimum_spacing_m": catalog.geography.min_spacing_m,
            "notes": catalog.geography.notes,
        }

    @app.get("/api/listings", response_model=ListingPage)
    async def listings(
        request: Request,
        query: Annotated[ListingQuery, Query()],
        repo: Annotated[ListingRepository, Depends(repository)],
    ):
        # Reject ambiguous repeated scalar parameters; only amenities is intentionally repeated.
        if any(
            len(request.query_params.getlist(key)) > 1 and key != "amenities"
            for key in request.query_params
        ):
            raise ServiceError("VALIDATION_ERROR", "Repeat only the amenities parameter.", 422)
        if query.region is not None and query.region not in {
            r.id for r in catalog.geography.regions
        }:
            raise ServiceError("INVALID_REGION", "Choose a region returned by /api/areas.", 422)
        filters = ListingFilters.model_validate(query.model_dump(exclude={"limit", "offset"}))
        return await repo.list(filters, limit=query.limit, offset=query.offset)

    @app.get("/api/listings/{listing_id}", response_model=Listing)
    async def detail(listing_id: UUID, repo: Annotated[ListingRepository, Depends(repository)]):
        result = await repo.get(listing_id)
        if result is None:
            raise ServiceError("LISTING_NOT_FOUND", "The requested listing was not found.", 404)
        return result

    return app


```

## backend/app/parsing.py

```python

from pydantic import ValidationError

from app.schemas import ListingFilters


class InvalidFilterOutput(ValueError):
    """Safe domain error: callers must not fall back to an unconstrained search."""


def parse_filter_output(payload: str) -> ListingFilters:
    # Existing strict parsing boundary retained for future M4 provider output.
    # Never eval output or repair broken JSON into potentially broader search constraints.
    if len(payload) > 16_000:
        raise InvalidFilterOutput("Search filters could not be validated. Please rephrase.")
    try:
        return ListingFilters.model_validate_json(payload)
    except ValidationError as exc:
        raise InvalidFilterOutput(
            "Search filters could not be validated. Please rephrase."
        ) from exc


```

## backend/app/repository.py

```python

from typing import Protocol
from uuid import UUID

from app.schemas import Listing, ListingFilters, ListingPage


class ListingRepository(Protocol):
    # Search depends on this contract, keeping SQLAlchemy and future data sources replaceable.
    async def list(
        self, filters: ListingFilters, *, limit: int = 30, offset: int = 0
    ) -> ListingPage: ...

    async def get(self, listing_id: UUID) -> Listing | None: ...


```

## backend/app/schemas.py

```python

from enum import Enum
from typing import Annotated, Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, allow_inf_nan=False)


class PropertyType(str, Enum):
    # Exact keys in frontend/src/model-manifest.json; studios use the apartment model.
    apartment = "apartment"
    townhouse = "townhouse"
    house = "house"
    loft = "loft"


class Amenity(str, Enum):
    wifi = "wifi"
    kitchen = "kitchen"
    workspace = "workspace"
    air_conditioning = "air_conditioning"
    parking = "parking"
    washer = "washer"
    balcony = "balcony"
    pet_friendly = "pet_friendly"
    crib = "crib"
    elevator = "elevator"


class Vibe(str, Enum):
    quiet = "quiet"
    nightlife = "nightlife"
    family_friendly = "family-friendly"
    romantic = "romantic"
    business = "business trip"
    budget = "budget"
    luxury = "luxury"
    scenic = "scenic"


MinorPrice = Annotated[int, Field(strict=True, ge=0, le=10_000_000)]
LocalImage = Annotated[str, Field(pattern=r"^/static/placeholders/[a-z-]+\.svg$")]


class Listing(Contract):
    id: UUID
    title: str = Field(min_length=8, max_length=120)
    pictures: list[LocalImage] = Field(min_length=1, max_length=8)
    description: str = Field(min_length=100, max_length=3000)
    price_minor: MinorPrice = Field(gt=0)
    currency: str = Field(pattern=r"^[A-Z]{3}$")
    rating: float = Field(ge=3.5, le=5)
    bedrooms: int = Field(strict=True, ge=0, le=5)
    max_guests: int = Field(strict=True, ge=1, le=10)
    amenities: list[Amenity] = Field(min_length=1, max_length=10)
    property_type: PropertyType
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    neighborhood: str = Field(min_length=1, max_length=80)
    region: str = Field(pattern=r"^[a-z]+(?:-[a-z]+)*$", max_length=80)
    vibes: list[Vibe] = Field(min_length=1, max_length=2)
    synthetic: bool = True

    @model_validator(mode="after")
    def coherent(self) -> Self:
        if not self.synthetic:
            raise ValueError("M2 accepts synthetic listings only")
        if self.max_guests > max(2, self.bedrooms * 2 + 2):
            raise ValueError("Guest capacity exceeds bedrooms plus one sofa bed")
        if self.property_type in (PropertyType.house, PropertyType.townhouse) and self.bedrooms < 1:
            raise ValueError("House and townhouse fixtures require a bedroom")
        for field in (self.amenities, self.vibes, self.pictures):
            if len(field) != len(set(field)):
                raise ValueError("Duplicate list values are not allowed")
        return self


class ListingFilters(Contract):
    price_min_minor: MinorPrice | None = None
    price_max_minor: MinorPrice | None = None
    guests: int | None = Field(default=None, strict=True, ge=1, le=10)
    bedrooms: int | None = Field(default=None, strict=True, ge=0, le=5)
    property_type: PropertyType | None = None
    region: str | None = Field(default=None, pattern=r"^[a-z]+(?:-[a-z]+)*$", max_length=80)
    amenities: list[Amenity] = Field(default_factory=list, max_length=10)

    @model_validator(mode="after")
    def ordered_prices(self) -> Self:
        if (
            self.price_min_minor is not None
            and self.price_max_minor is not None
            and self.price_min_minor > self.price_max_minor
        ):
            raise ValueError("Minimum price cannot exceed maximum price")
        if len(set(self.amenities)) != len(self.amenities):
            raise ValueError("Duplicate amenities are not allowed")
        return self


class ListingQuery(ListingFilters):
    # URL values are strings: conversion belongs at this HTTP boundary, not in
    # the reusable domain filters which will validate AI output in a later milestone.
    price_min_minor: int | None = Field(default=None, ge=0, le=10_000_000)
    price_max_minor: int | None = Field(default=None, ge=0, le=10_000_000)
    guests: int | None = Field(default=None, ge=1, le=10)
    bedrooms: int | None = Field(default=None, ge=0, le=5)
    limit: int = Field(default=30, ge=1, le=100)
    offset: int = Field(default=0, ge=0, le=1_000_000)

    @field_validator(
        "price_min_minor", "price_max_minor", "guests", "bedrooms", "limit", "offset", mode="before"
    )
    @classmethod
    def integer_query(cls, value):
        if value is not None and (
            isinstance(value, bool)
            or (isinstance(value, str) and (not value.isascii() or not value.isdecimal()))
        ):
            raise ValueError("Use nonnegative integer query values")
        return value


class ListingPage(Contract):
    items: list[Listing]
    total: int = Field(ge=0)
    limit: int = Field(ge=1, le=100)
    offset: int = Field(ge=0)


class HealthResponse(Contract):
    status: str = "ok"
    service: str


```

## backend/app/seeding.py

```python

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncEngine

from app.database import AmenityRow, Base, DatasetRow, ListingRow, session_factory
from app.dataset import Catalog, Dataset, validate_dataset
from app.errors import ServiceError


async def check_dataset(session, catalog: Catalog) -> dict:
    row = await session.get(DatasetRow, 1)
    if row is None:
        raise ServiceError(
            "DATASET_NOT_READY", "Generate and seed the dataset before using the API."
        )
    manifest = row.manifest
    if (
        manifest.get("currency") != catalog.currency
        or manifest.get("minor_units") != catalog.pricing.minor_units
        or manifest.get("regions_sha256") != catalog.geography.fingerprint
    ):
        raise ServiceError(
            "DATASET_CONFIG_MISMATCH",
            "The seeded dataset does not match server configuration. Regenerate and reseed.",
        )
    return manifest


async def seed_database(
    engine: AsyncEngine, dataset: Dataset, catalog: Catalog, *, replace: bool = False
) -> None:
    validate_dataset(dataset, catalog)
    # Explicit initialization is fine for this dev milestone. create_all is NOT a migration
    # system: production schema evolution should use reviewed Alembic migrations in M6.
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    async with session_factory(engine)() as session, session.begin():
        existing = await session.scalar(select(func.count()).select_from(ListingRow))
        if (existing or await session.get(DatasetRow, 1)) and not replace:
            raise ValueError("Database is already seeded; use --replace explicitly to replace it")
        if replace:
            # A single transaction prevents a failed seed from leaving a half-empty dataset.
            await session.execute(delete(AmenityRow))
            await session.execute(delete(ListingRow))
            await session.execute(delete(DatasetRow))
        for listing in dataset.listings:
            fields = listing.model_dump(mode="json", exclude={"amenities", "synthetic"})
            fields["id"] = listing.id
            session.add(
                ListingRow(
                    **fields, amenity_rows=[AmenityRow(amenity=a.value) for a in listing.amenities]
                )
            )
        session.add(
            DatasetRow(id=1, manifest=dataset.model_dump(mode="json", exclude={"listings"}))
        )


```

## backend/app/sql_repository.py

```python

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import AmenityRow, ListingRow
from app.schemas import Listing, ListingFilters, ListingPage


def to_listing(row: ListingRow) -> Listing:
    data = {column.name: getattr(row, column.name) for column in ListingRow.__table__.columns}
    data["amenities"] = sorted(a.amenity for a in row.amenity_rows)
    return Listing.model_validate(data)


class SQLListingRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list(
        self, filters: ListingFilters, *, limit: int = 30, offset: int = 0
    ) -> ListingPage:
        if not 1 <= limit <= 100 or not 0 <= offset <= 1_000_000:
            raise ValueError("Pagination is outside the supported range")
        clauses = []
        for value, clause in [
            (filters.price_min_minor, ListingRow.price_minor >= (filters.price_min_minor or 0)),
            (filters.price_max_minor, ListingRow.price_minor <= (filters.price_max_minor or 0)),
            (filters.guests, ListingRow.max_guests >= (filters.guests or 0)),
            (filters.bedrooms, ListingRow.bedrooms >= (filters.bedrooms or 0)),
        ]:
            if value is not None:  # Zero is a real filter, especially for price and bedrooms.
                clauses.append(clause)
        if filters.region is not None:
            clauses.append(ListingRow.region == filters.region)
        if filters.property_type is not None:
            clauses.append(ListingRow.property_type == filters.property_type.value)
        for amenity in filters.amenities:
            # Every requested amenity is mandatory; OR here would silently broaden a search.
            clauses.append(ListingRow.amenity_rows.any(AmenityRow.amenity == amenity.value))
        total = await self.session.scalar(
            select(func.count()).select_from(ListingRow).where(*clauses)
        )
        query = (
            select(ListingRow)
            .where(*clauses)
            .order_by(ListingRow.id)
            .offset(offset)
            .limit(limit)
            .options(selectinload(ListingRow.amenity_rows))
        )
        rows = (await self.session.scalars(query)).all()
        return ListingPage(
            items=[to_listing(row) for row in rows], total=total or 0, limit=limit, offset=offset
        )

    async def get(self, listing_id: UUID) -> Listing | None:
        row = await self.session.scalar(
            select(ListingRow)
            .where(ListingRow.id == listing_id)
            .options(selectinload(ListingRow.amenity_rows))
        )
        return None if row is None else to_listing(row)


```

## backend/config/descriptions.json

```json

{
  "quiet": [
    "An inward-facing sitting room keeps the pace deliberately slow, with a reading lamp beside a deep armchair. Evenings here revolve around a book and a pot of tea rather than a television left running.",
    "Soft curtains and a tucked-away breakfast corner give this stay a sheltered feel. The house notes ask guests to keep late arrivals quiet, making it a good match for early sleepers.",
    "A small collection of novels sits beside the window, and the dining table has room to spread out a puzzle. This is a retreat for unhurried mornings rather than group celebrations.",
    "Muted fabrics and uncluttered shelves make the living space feel restful after a busy day outside. A comfortable chair faces the courtyard side of the building for a slower evening indoors.",
    "The bedroom has blackout curtains and a bedside reading light for guests who like an early night. Shared-space etiquette favors conversation at a low volume after dinner.",
    "Morning coffee belongs at the little kitchen table, away from the main seating area. The restrained layout suits someone seeking personal space and a gentle daily routine.",
    "A woven rug softens the sitting area, while warm lamps replace harsh overhead light in the evening. Guests looking for a calm base can settle into a book without turning the room into a workstation.",
    "Board games and a reading basket take the place of party equipment in this thoughtfully simple home. The mood is peaceful and domestic, with room to unwind after exploring the city."
  ],
  "nightlife": [
    "The dining area is arranged for a relaxed meal before heading out for the evening. Blackout curtains help late sleepers recover, although the stay itself is not a party venue.",
    "Bold prints and a compact getting-ready mirror give the interior an energetic feel. This base suits visitors who plan their day around dinner reservations and an evening out.",
    "A little record shelf and warm lounge lighting set a sociable mood before dinner. Guests can enjoy the city's nightlife and return to a private place with clear quiet-hour rules.",
    "The sitting area works well for comparing evening plans over a snack. Expect a lively design sensibility rather than a secluded countryside atmosphere.",
    "Jewel-colored cushions and a breakfast bar make short city breaks feel festive. The layout is aimed at guests who spend evenings out and prefer leisurely starts the next morning.",
    "A full-length mirror and a generous entry bench make getting ready for a night out straightforward. The house rules still protect neighboring residents from late-night gatherings.",
    "Illustrated music posters give the lounge its personality without turning the home into a club. It is an easygoing base for travelers who want dinner, conversation, and a late return.",
    "Evening light catches the colorful artwork above the dining table. Guests who enjoy city entertainment can make this their starting point, while keeping celebrations outside the property."
  ],
  "family-friendly": [
    "A washable dining surface and a basket of children's books make shared routines easier. The living area leaves space for a quiet game while dinner is being prepared.",
    "Coat hooks sit at different heights and the entry has space to organize day bags. After an outing, the household can settle around the dining table instead of balancing meals on laps.",
    "Picture books and simple board games give younger visitors something to do between excursions. The atmosphere is practical and welcoming rather than filled with delicate display pieces.",
    "A separate eating corner helps preserve a bedtime routine when the rest of the household is still awake. Easy-care furnishings make the stay feel relaxed and lived in.",
    "The layout favors shared meals, with a kitchen that opens toward the gathering space. A basket for toys helps keep the floor clear when the day winds down.",
    "Family routines shape this home's small details, from a night-light to labeled kitchen storage. A comfortable common room gives everyone a place to regroup after sightseeing.",
    "The dining table doubles as a spot for drawing and travel journals. Soft seating and straightforward storage help the home work for a longer family visit.",
    "A welcoming entry bench makes shoes and jackets easier to manage at the end of a day out. The interior prioritizes useful surfaces and shared time over fragile decoration."
  ],
  "romantic": [
    "Two reading lamps frame a comfortable sitting nook, and the dining corner feels intimate after sunset. This stay lends itself to a slow breakfast and an evening spent talking over dinner.",
    "Linen textures and warm pools of light give the rooms a softly layered feel. The small dining table invites an unhurried meal without the formality of a restaurant.",
    "A window-side seat is the natural place to share coffee before heading out. In the evening, dimmable lamps turn the living area into a cozy retreat.",
    "The interior uses warm wood and subdued colors rather than busy patterns. It suits a couple who would rather cook together and linger over dessert than host a gathering.",
    "A pair of comfortable chairs faces a low table set aside for conversation. Gentle lighting makes this an appealing base for an anniversary weekend or a quiet city break.",
    "Textured blankets and a thoughtfully arranged breakfast spot make staying in feel like part of the trip. The atmosphere is intimate without relying on extravagant decoration.",
    "Art prints and a small flower vase give the dining corner a personal touch. The setting works well for visitors planning leisurely walks and evenings together indoors.",
    "An inviting sofa and soft bedside lighting make the home feel warm at the end of the day. There is enough room to slow down and enjoy a private meal together."
  ],
  "business trip": [
    "A dedicated desk faces a plain wall, with a task lamp for focused work. The dining space stays separate, helping a work trip keep some distinction between meetings and downtime.",
    "An ergonomic-style desk chair and accessible outlets make laptop sessions straightforward. The uncluttered entry gives visitors a place to prepare for the next day's appointments.",
    "The workspace is arranged for reading documents without clearing the kitchen table. After calls, a separate lounge chair provides a welcome change of posture.",
    "A task-lit desk anchors the practical interior, with space beside it for a notebook. This home favors a predictable workday routine over elaborate entertaining.",
    "The design leaves a calm background behind the desk for video meetings. A simple kitchen makes it easy to fit breakfast around an early start.",
    "A small desk organizer and sensible lighting give longer laptop sessions a more comfortable setting. The rest of the room stays relaxed enough to switch off after work.",
    "The work surface has room for a laptop and a paper planner side by side. Guests on a business trip can keep their materials organized without filling the dining area.",
    "Clear surfaces and a dedicated work corner make unpacking for a short assignment easy. The sitting area offers somewhere different to read or decompress between appointments."
  ],
  "budget": [
    "Simple furnishings keep the focus on useful space rather than decorative extras. Cooking a few meals at home is part of the appeal for guests watching their travel budget.",
    "This is a modest city base with a straightforward layout and practical storage. It suits travelers who prefer spending on experiences outside rather than on luxury interiors.",
    "A small dining setup and durable furniture cover the essentials without fuss. The mood is informal, making it a sensible choice for a cost-conscious short stay.",
    "The interior is compact and deliberately uncomplicated, with just enough furniture to settle in comfortably. Guests seeking value will appreciate having their own cooking space.",
    "Functional shelves and an easy-care seating area make this an economical place to unpack. The emphasis is on daily convenience rather than premium finishes or concierge-style extras.",
    "Good use of a modest footprint gives the home a practical character. Bringing groceries and preparing breakfast here can help a city visit feel less expensive.",
    "The rooms use familiar, sturdy furniture and a restrained amount of decoration. This stay is intended for guests who need a useful base more than a showcase interior.",
    "A simple table, comfortable seating, and clear storage define the living area. Travelers comparing value can choose a home that concentrates on essentials."
  ],
  "luxury": [
    "Layered lighting and carefully spaced furniture give the lounge a generous, composed feel. Rich fabrics and substantial dining chairs make an evening at home feel considered.",
    "Stone-look surfaces and warm cabinetry create a polished kitchen setting. The living area carries the same attention to finish, with inviting seating and restrained artwork.",
    "A spacious-feeling lounge pairs textured upholstery with sculptural lamps. This stay is designed for visitors who enjoy spending time in their accommodation as well as exploring outside.",
    "The dining area has a more formal character, with coordinated tableware and comfortable chairs. A carefully edited palette gives the rest of the home a calm, premium feel.",
    "Thick curtains and layered bedding soften an interior built around warm wood tones. The rooms favor tactile comfort and thoughtful details over visual clutter.",
    "Generous seating and well-placed lamps make the lounge welcoming at different times of day. The overall impression is quietly upscale rather than showy.",
    "Subtle artwork and carefully chosen finishes give this home a curated identity. Visitors planning a special trip can enjoy an interior with more attention to comfort and presentation.",
    "A beautifully arranged dining corner sets the tone for lingering meals. Soft textiles and coordinated lighting extend that feeling through the rest of the home."
  ],
  "scenic": [
    "A furnished balcony gives morning coffee a place outdoors above the everyday street scene. The living area keeps the window wall open so changing daylight becomes part of the room.",
    "Light moves across the dining table during the day, drawing attention toward the balcony doors. This stay suits guests who enjoy sketching rooflines and watching the neighborhood wake up.",
    "A chair by the balcony entrance offers a comfortable perch even when the weather keeps you inside. The appeal is neighborhood outlook and daylight, not a promised landmark panorama.",
    "The outdoor seating area makes a simple breakfast feel like a small occasion. Inside, pale fabrics and an uncluttered window line keep attention on the changing sky.",
    "Broad windows bring a sense of openness to the sitting area, with a balcony for a breath of air. Guests who like photographing city textures will find the everyday roofscape appealing.",
    "The balcony is set up for sitting with a book rather than hosting a crowd. An open-feeling lounge makes it easy to enjoy the shifting light from indoors as well.",
    "A pair of outdoor chairs provides a place to pause between excursions. The outlook is intentionally described as a neighborhood scene, without promising waterfront or landmark views.",
    "The main sitting area is organized around natural light and access to the balcony. It makes a gentle setting for a late breakfast or watching the evening colors settle."
  ]
}


```

## backend/config/images.json

```json

{
  "apartment": [
    "/static/placeholders/apartment.svg"
  ],
  "townhouse": [
    "/static/placeholders/townhouse.svg"
  ],
  "house": [
    "/static/placeholders/house.svg"
  ],
  "loft": [
    "/static/placeholders/loft.svg"
  ]
}


```

## backend/config/pricing.json

```json

{
  "USD": {
    "minor_units": 2,
    "region_base_minor": {
      "manhattan": 20500,
      "brooklyn": 16000,
      "queens": 13000,
      "jersey-city": 14500,
      "hoboken": 17500
    }
  }
}


```

## backend/config/regions.json

```json

{
  "version": 1,
  "coordinate_order": "longitude,latitude",
  "min_spacing_m": 75,
  "notes": "Hand-drawn conservative inland demo zones, not borough boundaries or a complete land-use mask. Exclusions deliberately overestimate selected parks. Review the GeoJSON against a basemap.",
  "regions": [
    {
      "id": "manhattan",
      "name": "Manhattan",
      "neighborhood": "Midtown and West Side",
      "center": [
        -73.985,
        40.757
      ],
      "polygon": [
        [
          -74.002,
          40.741
        ],
        [
          -73.987,
          40.741
        ],
        [
          -73.972,
          40.762
        ],
        [
          -73.965,
          40.785
        ],
        [
          -73.979,
          40.779
        ],
        [
          -73.987,
          40.765
        ],
        [
          -74.002,
          40.741
        ]
      ],
      "exclusions": [
        {
          "name": "Central Park (conservative envelope)",
          "polygon": [
            [
              -73.983,
              40.767
            ],
            [
              -73.96,
              40.802
            ],
            [
              -73.947,
              40.797
            ],
            [
              -73.971,
              40.763
            ],
            [
              -73.983,
              40.767
            ]
          ]
        },
        {
          "name": "Bryant Park and library block",
          "polygon": [
            [
              -73.9857,
              40.7518
            ],
            [
              -73.9805,
              40.7518
            ],
            [
              -73.9805,
              40.7552
            ],
            [
              -73.9857,
              40.7552
            ],
            [
              -73.9857,
              40.7518
            ]
          ]
        },
        {
          "name": "Madison Square Park",
          "polygon": [
            [
              -73.9899,
              40.7407
            ],
            [
              -73.9861,
              40.7407
            ],
            [
              -73.9861,
              40.7439
            ],
            [
              -73.9899,
              40.7439
            ],
            [
              -73.9899,
              40.7407
            ]
          ]
        },
        {
          "name": "Chelsea Park",
          "polygon": [
            [
              -74.0035,
              40.7484
            ],
            [
              -73.9998,
              40.7484
            ],
            [
              -73.9998,
              40.7509
            ],
            [
              -74.0035,
              40.7509
            ],
            [
              -74.0035,
              40.7484
            ]
          ]
        },
        {
          "name": "Lincoln Center campus",
          "polygon": [
            [
              -73.9877,
              40.771
            ],
            [
              -73.9818,
              40.771
            ],
            [
              -73.9818,
              40.7757
            ],
            [
              -73.9877,
              40.7757
            ],
            [
              -73.9877,
              40.771
            ]
          ]
        }
      ]
    },
    {
      "id": "brooklyn",
      "name": "Brooklyn",
      "neighborhood": "Park Slope",
      "center": [
        -73.981,
        40.674
      ],
      "polygon": [
        [
          -73.984,
          40.67
        ],
        [
          -73.978,
          40.67
        ],
        [
          -73.978,
          40.683
        ],
        [
          -73.984,
          40.683
        ],
        [
          -73.984,
          40.67
        ]
      ],
      "exclusions": [
        {
          "name": "Prospect Park (conservative envelope)",
          "polygon": [
            [
              -73.977,
              40.65
            ],
            [
              -73.961,
              40.65
            ],
            [
              -73.961,
              40.673
            ],
            [
              -73.977,
              40.673
            ],
            [
              -73.977,
              40.65
            ]
          ]
        },
        {
          "name": "Washington Park and playground",
          "polygon": [
            [
              -73.987,
              40.6705
            ],
            [
              -73.984,
              40.6705
            ],
            [
              -73.984,
              40.674
            ],
            [
              -73.987,
              40.674
            ],
            [
              -73.987,
              40.6705
            ]
          ]
        },
        {
          "name": "J J Byrne eastern playground",
          "polygon": [
            [
              -73.9843,
              40.671
            ],
            [
              -73.9828,
              40.671
            ],
            [
              -73.9828,
              40.6724
            ],
            [
              -73.9843,
              40.6724
            ],
            [
              -73.9843,
              40.671
            ]
          ]
        },
        {
          "name": "Park Slope playground",
          "polygon": [
            [
              -73.9835,
              40.6745
            ],
            [
              -73.9815,
              40.6745
            ],
            [
              -73.9815,
              40.6759
            ],
            [
              -73.9835,
              40.6759
            ],
            [
              -73.9835,
              40.6745
            ]
          ]
        }
      ]
    },
    {
      "id": "queens",
      "name": "Queens",
      "neighborhood": "Astoria",
      "center": [
        -73.922,
        40.765
      ],
      "polygon": [
        [
          -73.928,
          40.757
        ],
        [
          -73.916,
          40.757
        ],
        [
          -73.916,
          40.774
        ],
        [
          -73.928,
          40.774
        ],
        [
          -73.928,
          40.757
        ]
      ],
      "exclusions": [
        {
          "name": "Athens Square",
          "polygon": [
            [
              -73.9223,
              40.7661
            ],
            [
              -73.9201,
              40.7661
            ],
            [
              -73.9201,
              40.7685
            ],
            [
              -73.9223,
              40.7685
            ],
            [
              -73.9223,
              40.7661
            ]
          ]
        },
        {
          "name": "Sean's Place playground",
          "polygon": [
            [
              -73.9215,
              40.7592
            ],
            [
              -73.9191,
              40.7592
            ],
            [
              -73.9191,
              40.7614
            ],
            [
              -73.9215,
              40.7614
            ],
            [
              -73.9215,
              40.7592
            ]
          ]
        },
        {
          "name": "Astoria Park (outside sampling zone)",
          "polygon": [
            [
              -73.926,
              40.776
            ],
            [
              -73.92,
              40.776
            ],
            [
              -73.92,
              40.783
            ],
            [
              -73.926,
              40.783
            ],
            [
              -73.926,
              40.776
            ]
          ]
        }
      ]
    },
    {
      "id": "jersey-city",
      "name": "Jersey City",
      "neighborhood": "Downtown Jersey City",
      "center": [
        -74.047,
        40.722
      ],
      "polygon": [
        [
          -74.053,
          40.714
        ],
        [
          -74.041,
          40.714
        ],
        [
          -74.041,
          40.7295
        ],
        [
          -74.053,
          40.7295
        ],
        [
          -74.053,
          40.714
        ]
      ],
      "exclusions": [
        {
          "name": "Van Vorst Park",
          "polygon": [
            [
              -74.0493,
              40.7175
            ],
            [
              -74.0461,
              40.7175
            ],
            [
              -74.0461,
              40.72
            ],
            [
              -74.0493,
              40.72
            ],
            [
              -74.0493,
              40.7175
            ]
          ]
        },
        {
          "name": "Hamilton Park",
          "polygon": [
            [
              -74.047,
              40.7263
            ],
            [
              -74.043,
              40.7263
            ],
            [
              -74.043,
              40.73
            ],
            [
              -74.047,
              40.73
            ],
            [
              -74.047,
              40.7263
            ]
          ]
        },
        {
          "name": "Mary Benson Park",
          "polygon": [
            [
              -74.054,
              40.7208
            ],
            [
              -74.051,
              40.7208
            ],
            [
              -74.051,
              40.7233
            ],
            [
              -74.054,
              40.7233
            ],
            [
              -74.054,
              40.7208
            ]
          ]
        }
      ]
    },
    {
      "id": "hoboken",
      "name": "Hoboken",
      "neighborhood": "Central Hoboken",
      "center": [
        -74.033,
        40.745
      ],
      "polygon": [
        [
          -74.038,
          40.738
        ],
        [
          -74.029,
          40.738
        ],
        [
          -74.029,
          40.752
        ],
        [
          -74.038,
          40.752
        ],
        [
          -74.038,
          40.738
        ]
      ],
      "exclusions": [
        {
          "name": "Church Square Park",
          "polygon": [
            [
              -74.0346,
              40.7404
            ],
            [
              -74.0314,
              40.7404
            ],
            [
              -74.0314,
              40.743
            ],
            [
              -74.0346,
              40.743
            ],
            [
              -74.0346,
              40.7404
            ]
          ]
        },
        {
          "name": "Columbus Park",
          "polygon": [
            [
              -74.0353,
              40.7471
            ],
            [
              -74.032,
              40.7471
            ],
            [
              -74.032,
              40.7501
            ],
            [
              -74.0353,
              40.7501
            ],
            [
              -74.0353,
              40.7471
            ]
          ]
        },
        {
          "name": "JFK stadium and recreation grounds",
          "polygon": [
            [
              -74.037,
              40.7432
            ],
            [
              -74.0332,
              40.7432
            ],
            [
              -74.0332,
              40.7462
            ],
            [
              -74.037,
              40.7462
            ],
            [
              -74.037,
              40.7432
            ]
          ]
        }
      ]
    }
  ]
}


```

## backend/static/placeholders/apartment.svg

```xml

<svg xmlns="http://www.w3.org/2000/svg" width="320" height="240" viewBox="0 0 320 240" role="img" aria-label="Synthetic apartment placeholder"><rect width="320" height="240" rx="12" fill="#14232d"/><g fill="#607e8b"><rect x="118" y="45" width="84" height="130" rx="5"/><path d="M132 63h16v18h-16zm40 0h16v18h-16zm-40 34h16v18h-16zm40 0h16v18h-16zm-40 34h16v18h-16zm40 0h16v18h-16z" fill="#b9edda"/></g><text x="160" y="207" text-anchor="middle" fill="#cce9dc" font-size="16" font-family="sans-serif">APARTMENT · SYNTHETIC</text></svg>


```

## backend/static/placeholders/house.svg

```xml

<svg xmlns="http://www.w3.org/2000/svg" width="320" height="240" viewBox="0 0 320 240" role="img" aria-label="Synthetic house placeholder"><rect width="320" height="240" rx="12" fill="#14232d"/><g fill="#607e8b"><path d="M75 98l85-62 85 62-14 5v72H89v-72z"/><path d="M113 110h26v26h-26zm69 0h26v26h-26zm-32 28h22v37h-22z" fill="#b9edda"/></g><text x="160" y="207" text-anchor="middle" fill="#cce9dc" font-size="16" font-family="sans-serif">HOUSE · SYNTHETIC</text></svg>


```

## backend/static/placeholders/loft.svg

```xml

<svg xmlns="http://www.w3.org/2000/svg" width="320" height="240" viewBox="0 0 320 240" role="img" aria-label="Synthetic loft placeholder"><rect width="320" height="240" rx="12" fill="#14232d"/><g fill="#607e8b"><path d="M80 90l53-30v30l53-30v30l53-30v115H80z"/><path d="M99 108h35v22H99zm53 0h35v22h-35zm53 0h17v22h-17zm-70 38h43v29h-43z" fill="#b9edda"/></g><text x="160" y="207" text-anchor="middle" fill="#cce9dc" font-size="16" font-family="sans-serif">LOFT · SYNTHETIC</text></svg>


```

## backend/static/placeholders/townhouse.svg

```xml

<svg xmlns="http://www.w3.org/2000/svg" width="320" height="240" viewBox="0 0 320 240" role="img" aria-label="Synthetic townhouse placeholder"><rect width="320" height="240" rx="12" fill="#14232d"/><g fill="#607e8b"><path d="M105 76l55-37 55 37v99H105z"/><path d="M126 91h22v25h-22zm46 0h22v25h-22zm-21 46h22v38h-22z" fill="#b9edda"/></g><text x="160" y="207" text-anchor="middle" fill="#cce9dc" font-size="16" font-family="sans-serif">TOWNHOUSE · SYNTHETIC</text></svg>


```

## backend/tests/conftest.py

```python

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.database import make_engine, session_factory
from app.dataset import Catalog
from app.generator import GenerationOptions, generate
from app.main import create_app
from app.seeding import seed_database


@pytest.fixture(scope="session")
def catalog():
    return Catalog(Settings(_env_file=None))


@pytest.fixture(scope="session")
def dataset(catalog):
    return generate(catalog, GenerationOptions(count=300, seed=42))


@pytest.fixture
async def database(tmp_path, dataset, catalog):
    url = f"sqlite+aiosqlite:///{(tmp_path / 'test.db').as_posix()}"
    engine = make_engine(url)
    await seed_database(engine, dataset, catalog)
    yield engine, Settings(_env_file=None, database_url=url)
    await engine.dispose()


@pytest.fixture
async def session(database):
    async with session_factory(database[0])() as session:
        yield session


@pytest.fixture
def client(database):
    with TestClient(create_app(database[1])) as client:
        yield client


```

## backend/tests/test_api.py

```python

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
    assert client.post("/api/search").status_code == 404  # No M4 endpoint sneaks into M2.


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


```

## backend/tests/test_contracts.py

```python

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


```

## backend/tests/test_generator.py

```python

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


```

## backend/tests/test_repository.py

```python

import pytest
from sqlalchemy import func, select, update
from sqlalchemy.dialects import postgresql
from sqlalchemy.exc import IntegrityError
from sqlalchemy.schema import CreateTable

from app.database import Base, ListingRow
from app.schemas import ListingFilters
from app.seeding import seed_database
from app.sql_repository import SQLListingRepository


def matches(item, filters):
    return (
        (filters.price_min_minor is None or item.price_minor >= filters.price_min_minor)
        and (filters.price_max_minor is None or item.price_minor <= filters.price_max_minor)
        and (filters.guests is None or item.max_guests >= filters.guests)
        and (filters.bedrooms is None or item.bedrooms >= filters.bedrooms)
        and (filters.region is None or item.region == filters.region)
        and (filters.property_type is None or item.property_type == filters.property_type)
        and set(filters.amenities) <= set(item.amenities)
    )


@pytest.mark.parametrize(
    "data",
    [
        {},
        {"price_min_minor": 15000},
        {"price_max_minor": 25000},
        {"price_max_minor": 0},
        {"guests": 4},
        {"bedrooms": 2},
        {"bedrooms": 0},
        {"property_type": "townhouse"},
        {"region": "queens"},
        {"amenities": ["washer", "workspace"]},
        {
            "price_min_minor": 10000,
            "price_max_minor": 40000,
            "guests": 2,
            "bedrooms": 1,
            "property_type": "apartment",
            "region": "brooklyn",
            "amenities": ["wifi", "kitchen"],
        },
    ],
)
async def test_filters_apply_before_pagination(session, dataset, data):
    filters = ListingFilters.model_validate(data)
    repo = SQLListingRepository(session)
    expected = sorted([x for x in dataset.listings if matches(x, filters)], key=lambda x: x.id)
    result = await repo.list(filters, limit=7, offset=3)
    assert result.total == len(expected)
    assert [x.id for x in result.items] == [x.id for x in expected[3:10]]
    assert all(matches(x, filters) for x in result.items)


async def test_price_boundaries_get_and_pagination(session, dataset):
    from uuid import UUID

    repo = SQLListingRepository(session)
    target = dataset.listings[0]
    result = await repo.list(
        ListingFilters(price_min_minor=target.price_minor, price_max_minor=target.price_minor),
        limit=100,
    )
    assert target.id in [x.id for x in result.items]
    assert (await repo.get(target.id)).model_dump() == target.model_dump()
    assert await repo.get(UUID(int=0)) is None
    first = await repo.list(ListingFilters(), limit=100)
    second = await repo.list(ListingFilters(), limit=100, offset=100)
    assert not set(x.id for x in first.items) & set(x.id for x in second.items)
    empty = await repo.list(ListingFilters(), offset=1000)
    assert empty.items == [] and empty.total == 300


async def test_database_constraints_are_a_second_boundary(session, dataset):
    with pytest.raises(IntegrityError):
        await session.execute(
            update(ListingRow).where(ListingRow.id == dataset.listings[0].id).values(price_minor=-1)
        )
        await session.commit()
    await session.rollback()
    with pytest.raises(IntegrityError):
        await session.execute(
            update(ListingRow)
            .where(ListingRow.id == dataset.listings[0].id)
            .values(property_type="studio")
        )
        await session.commit()
    await session.rollback()


async def test_seed_refuses_unrequested_replacement(database, dataset, catalog):
    with pytest.raises(ValueError, match="already seeded"):
        await seed_database(database[0], dataset, catalog)
    from app.database import session_factory

    async with session_factory(database[0])() as session:
        assert await session.scalar(select(func.count()).select_from(ListingRow)) == 300
    await seed_database(database[0], dataset, catalog, replace=True)
    async with session_factory(database[0])() as session:
        assert await session.scalar(select(func.count()).select_from(ListingRow)) == 300


def test_schema_compiles_for_postgres():
    # A portability check, not a substitute for running against a real Postgres server.
    for table in Base.metadata.sorted_tables:
        assert str(CreateTable(table).compile(dialect=postgresql.dialect()))


```
