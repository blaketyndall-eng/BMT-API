from fastapi import FastAPI

from apps.api.routes.admin import router as admin_router
from apps.api.routes.agent_evals import router as agent_evals_router
from apps.api.routes.agents import router as agents_router
from apps.api.routes.compare import router as compare_router
from apps.api.routes.products import router as products_router
from apps.api.routes.source_promotion import router as source_promotion_router
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
app.include_router(agent_evals_router)
app.include_router(source_promotion_router)
app.include_router(products_router)
app.include_router(compare_router)
app.include_router(agents_router)


@app.get("/healthz", tags=["system"])
def healthcheck() -> dict[str, str]:
    settings = get_settings()
    return {
        "status": "ok",
        "service": "api",
        "environment": settings.environment,
    }
