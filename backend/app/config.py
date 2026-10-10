from pathlib import Path

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    # Backend-local settings avoid inheriting the superseded root M1 AI settings.
    model_config = SettingsConfigDict(env_file=BACKEND / ".env", extra="ignore")

    app_name: str = "StayScape"
    database_url: str = f"sqlite+aiosqlite:///{(BACKEND / 'data/stayscape-m2.db').as_posix()}"
    currency_code: str = Field(default="USD", pattern=r"^[A-Z]{3}$")
    regions_file: Path = BACKEND / "config/regions.json"
    pricing_file: Path = BACKEND / "config/pricing.json"
    images_file: Path = BACKEND / "config/images.json"
    # Offline by default: entering a key alone never enables provider spending.
    search_demo_mode: bool = True
    search_base_url: str = "https://api.groq.com/openai/v1"
    search_api_key: str = ""
    search_model: str = ""
    search_timeout_seconds: float = Field(default=6, ge=1, le=15)
    search_index_file: Path = BACKEND / "data/search-index.json"
    search_examples_file: Path = BACKEND / "config/search-examples.json"
    search_rate_per_minute: int = Field(default=20, ge=1, le=120)
    corpus_file: Path = BACKEND / "config/descriptions.json"
    cors_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:5173", "http://127.0.0.1:5173"],
        # Keep older local .env files working; the documented deployment name takes precedence.
        validation_alias=AliasChoices("ALLOWED_ORIGINS", "CORS_ORIGINS", "cors_origins"),
    )

    @field_validator("database_url")
    @classmethod
    def async_driver_only(cls, value: str) -> str:
        if not value.startswith(("sqlite+aiosqlite:///", "postgresql+asyncpg://")):
            raise ValueError("Use sqlite+aiosqlite or postgresql+asyncpg")
        return value
