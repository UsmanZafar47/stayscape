from pydantic import ValidationError

from app.schemas import ListingFilters


class InvalidFilterOutput(ValueError):
    """Safe domain error: callers must not fall back to an unconstrained search."""


def parse_filter_output(payload: str) -> ListingFilters:
    # Existing strict parsing boundary retained for future M4 provider output.
    # Never eval output or repair broken JSON into potentially broader search constraints.
    if len(payload) > 16_000:
        raise InvalidFilterOutput("Search filters could not be validated. Please rephrase.")
    try:
        return ListingFilters.model_validate_json(payload)
    except ValidationError as exc:
        raise InvalidFilterOutput(
            "Search filters could not be validated. Please rephrase."
        ) from exc
