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
