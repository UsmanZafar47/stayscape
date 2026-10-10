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
from app.search import SearchService, SearchResponse
from app.search_parser import SearchRequest

logger = logging.getLogger(__name__)


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings if settings is not None else Settings()
    catalog = Catalog(settings)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        engine = make_engine(settings.database_url)
        app.state.sessions = session_factory(engine)
        app.state.search = SearchService(settings)
        try:
            yield
        finally:
            await app.state.search.provider.client.aclose()
            await engine.dispose()

    app = FastAPI(title=settings.app_name, version="0.2.0", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST"],
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

    @app.get("/api/search/examples")
    async def search_examples(request: Request):
        return {"queries": [x["query"] for x in request.app.state.search.examples],
                "demo_mode": settings.search_demo_mode}

    @app.post("/api/search", response_model=SearchResponse)
    async def search(body: SearchRequest, request: Request,
                     repo: Annotated[ListingRepository, Depends(repository)]):
        service = request.app.state.search
        # Trust the direct client only. Proxy-header trust/deployment is deliberately outside M4.
        service.rate_limit(request.client.host if request.client else "unknown")
        from pydantic import ValidationError
        try:
            return await service.search(body, repo)
        except ValidationError as exc:
            raise ServiceError("INVALID_SEARCH", "The interpreted filters are invalid. Check prices/counts and rephrase.", 422) from exc

    return app
