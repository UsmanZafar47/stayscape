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
