from fastapi import FastAPI

from apps.api.routes.vendors import router as vendors_router
from packages.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title="BMT API",
    version="0.1.0",
    description="Evidence-backed vendor understanding API.",
)

app.include_router(vendors_router)


@app.get("/healthz", tags=["system"])
def healthcheck() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "api",
        "environment": settings.environment,
    }
