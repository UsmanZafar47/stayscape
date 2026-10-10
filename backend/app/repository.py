from typing import Protocol
from uuid import UUID

from app.schemas import Listing, ListingFilters, ListingPage


class ListingRepository(Protocol):
    # Search depends on this contract, keeping SQLAlchemy and future data sources replaceable.
    async def list(
        self, filters: ListingFilters, *, limit: int = 30, offset: int = 0
    ) -> ListingPage: ...

    async def get(self, listing_id: UUID) -> Listing | None: ...
