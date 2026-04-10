from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="BMT_API_", extra="ignore")

    environment: str = "local"
    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/bmt_api"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
