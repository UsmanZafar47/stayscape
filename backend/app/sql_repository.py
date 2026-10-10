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
