from fastapi import FastAPI

from apps.api.routes.admin import router as admin_router
from apps.api.routes.compare import router as compare_router
from apps.api.routes.products import router as products_router
from apps.api.routes.vendors import router as vendors_router
from packages.core.config import get_settings
from packages.observability.middleware import RequestTracingMiddleware

app = FastAPI(
    title="BMT API",
    version="0.1.0",
    description="Evidence-backed vendor understanding API.",
)
app.add_middleware(RequestTracingMiddleware)

app.include_router(vendors_router)
app.include_router(admin_router)
app.include_router(products_router)
app.include_router(compare_router)


@app.get("/healthz", tags=["system"])
def healthcheck() -> dict[str, str]:
    settings = get_settings()
    return {
        "status": "ok",
        "service": "api",
        "environment": settings.environment,
    }
