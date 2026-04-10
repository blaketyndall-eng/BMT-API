import re

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    environment: str = Field(
        default="local",
        validation_alias=AliasChoices("BMT_API_ENVIRONMENT", "BMT_API_ENV"),
    )
    database_url: str = Field(
        default="postgresql+psycopg://postgres:postgres@localhost:5432/bmt_api",
        validation_alias=AliasChoices("BMT_API_DATABASE_URL", "DATABASE_URL"),
    )


def _normalize_database_url(url: str) -> str:
    """Normalize a PostgreSQL URL to use the psycopg driver.

    Railway injects plain ``postgresql://`` or ``postgres://`` URLs at runtime,
    which SQLAlchemy maps to the legacy ``psycopg2`` driver by default. Since
    only ``psycopg`` (v3) is installed, any URL that lacks an explicit driver
    specifier is rewritten to use ``postgresql+psycopg://``.

    URLs that already carry an explicit driver (e.g. ``+psycopg2`` or
    ``+psycopg``) are returned unchanged.
    """
    if re.match(r"^postgres(?:ql)?://", url):
        return re.sub(r"^postgres(?:ql)?://", "postgresql+psycopg://", url)
    return url


def get_settings() -> Settings:
    settings = Settings()
    settings.database_url = _normalize_database_url(settings.database_url)
    return settings
