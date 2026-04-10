import re
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="BMT_API_", extra="ignore")

    environment: str = "local"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/bmt_api"


def _normalize_database_url(url: str) -> str:
    """Normalize a PostgreSQL URL to use the psycopg driver.

    Railway injects plain ``postgresql://`` or ``postgres://`` URLs at runtime,
    which SQLAlchemy maps to the legacy ``psycopg2`` driver by default.  Since
    only ``psycopg`` (v3) is installed, any URL that lacks an explicit driver
    specifier is rewritten to use ``postgresql+psycopg://``.

    URLs that already carry an explicit driver (e.g. ``+psycopg2`` or
    ``+psycopg``) are returned unchanged.
    """
    if re.match(r"^postgres(?:ql)?://", url):
        return re.sub(r"^postgres(?:ql)?://", "postgresql+psycopg://", url)
    return url


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings()
    settings.database_url = _normalize_database_url(settings.database_url)
    return settings
