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
