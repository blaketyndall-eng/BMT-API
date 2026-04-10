from functools import lru_cache

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from packages.core.config import get_settings


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    settings = get_settings()
    return create_engine(settings.database_url, future=True)


def SessionLocal():
    return sessionmaker(bind=get_engine(), autoflush=False, autocommit=False, future=True)()


class Base(DeclarativeBase):
    pass
