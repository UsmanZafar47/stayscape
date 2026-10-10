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
    # SQLite URI mode=ro is an image-bundled dataset, not a writable filesystem path.
    if sqlite and parsed.query.get("mode") != "ro" and parsed.database and parsed.database != ":memory:":
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
