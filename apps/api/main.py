import logging

from fastapi import FastAPI

from apps.api.routes.vendors import router as vendors_router
from packages.core.config import get_settings

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="BMT API",
    version="0.1.0",
    description="Evidence-backed vendor understanding API.",
)

app.include_router(vendors_router)


@app.get("/healthz", tags=["system"])
def healthcheck() -> dict[str, str]:
    settings = get_settings()
    logger.debug(
        "/healthz — settings.environment=%r settings.database_url=%r",
        settings.environment,
        settings.database_url,
    )
    return {
        "status": "ok",
        "service": "api",
        "environment": settings.environment,
    }
