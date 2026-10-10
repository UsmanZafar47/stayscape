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
