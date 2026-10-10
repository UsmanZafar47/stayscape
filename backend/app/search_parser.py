"""A deliberately small interpretation boundary, shared by live search and demo preparation."""
import re
from decimal import Decimal
from typing import Literal

from pydantic import Field, field_validator

from app.schemas import Contract, ListingFilters, Vibe

REGIONS = ("manhattan", "brooklyn", "queens", "jersey-city", "hoboken")


class SearchIntent(ListingFilters):
    region: Literal["manhattan", "brooklyn", "queens", "jersey-city", "hoboken"] | None = None
    vibes: list[Vibe] = Field(default_factory=list, max_length=8)

    @field_validator("vibes")
    @classmethod
    def unique_vibes(cls, value):
        if len(value) != len(set(value)):
            raise ValueError("Duplicate vibes")
        return value

    def filters(self) -> ListingFilters:
        return ListingFilters.model_validate(self.model_dump(exclude={"vibes"}))


class SearchRequest(Contract):
    query: str = Field(min_length=1, max_length=500, strict=True)
    demo: bool = Field(default=False, strict=True)


VIBE_WORDS = {
    "quiet": ("quiet", "calm", "peaceful", "reading", "restful"),
    "nightlife": ("nightlife", "lively", "night out"),
    "family-friendly": ("family", "children", "kids"),
    "romantic": ("romantic", "couple", "couples"),
    "business trip": ("business", "work trip", "remote work"),
    "budget": ("budget", "cheap", "affordable"),
    "luxury": ("luxury", "upscale", "luxurious"),
    "scenic": ("scenic", "view", "views"),
}
AMENITY_WORDS = {
    "wifi": ("wifi", "wi-fi", "internet"), "kitchen": ("kitchen",),
    "workspace": ("workspace", "desk"), "air_conditioning": ("air conditioning", "ac"),
    "parking": ("parking",), "washer": ("washer", "laundry"), "balcony": ("balcony",),
    "pet_friendly": ("pet friendly", "pet-friendly", "dog", "pets"),
    "crib": ("crib",), "elevator": ("elevator", "lift"),
}


def mentions(text: str, words: tuple[str, ...]) -> bool:
    # Ignore simple negations; more complex language is explicitly outside fallback guarantees.
    return any(re.search(r"\b" + re.escape(word) + r"\b", text) for word in words)


def parse_rules(query: str) -> SearchIntent:
    text = query.lower().replace(",", "")
    text = re.sub(r"\b(?:no|without|not)\s+(?:\w+-?\w*\s+)?(?:parking|wifi|kitchen|balcony|pets|luxury|nightlife)\b", "", text)
    data: dict = {}
    amount = r"\$?\s*(\d+(?:\.\d{1,2})?)"
    cents = lambda value: int(Decimal(value) * 100)
    between = re.search(r"(?:between|from)\s+" + amount + r"\s*(?:and|to|-)\s*" + amount, text)
    if between:
        data.update(price_min_minor=cents(between[1]), price_max_minor=cents(between[2]))
    else:
        upper = re.search(r"(?:under|below|less than|up to|at most|max(?:imum)?|budget(?: of)?)\s+" + amount, text)
        if not upper:
            upper = re.search(amount + r"\s*(?:max|maximum|per night|a night|/night)\b", text)
        lower = re.search(r"(?:over|above|at least|min(?:imum)?)\s+\$\s*(\d+(?:\.\d{1,2})?)", text)
        if upper:
            data["price_max_minor"] = cents(upper[1])
        if lower:
            data["price_min_minor"] = cents(lower[1])
    for field, pattern in [("guests", r"\b(\d+)\s*(?:guests?|people|persons?|adults?)\b"),
                           ("bedrooms", r"\b(\d+)\s*[- ]?(?:bedrooms?|beds?|br)\b")]:
        match = re.search(pattern, text)
        if match:
            data[field] = int(match[1])
    for region in REGIONS:
        if mentions(text, (region, region.replace("-", " "))):
            data["region"] = region
            break
    for kind in ("apartment", "townhouse", "house", "loft"):
        if mentions(text, (kind, kind + "s")):
            data["property_type"] = kind
            break
    if mentions(text, ("studio",)):
        data.update(property_type="apartment", bedrooms=0)
    data["amenities"] = [key for key, words in AMENITY_WORDS.items() if mentions(text, words)]
    data["vibes"] = [key for key, words in VIBE_WORDS.items() if mentions(text, words)]
    # Same bounds and strict integer-money contract as ordinary SQL filters; never clamp bad input.
    return SearchIntent.model_validate(data)
