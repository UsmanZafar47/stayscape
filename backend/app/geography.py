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
