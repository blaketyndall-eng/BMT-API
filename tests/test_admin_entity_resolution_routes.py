from fastapi.testclient import TestClient

from apps.api.main import app
from packages.core.deps import get_db


class DummyEntityResolutionService:
    def __init__(self, _db: object) -> None:
        pass

    def resolve(self, payload):
        return type(
            "Resp",
            (),
            {
                "model_dump": lambda self: {
                    "vendor_domain": payload.vendor_domain,
                    "root_url": payload.root_url,
                    "artifact_slug": payload.artifact_slug,
                    "vendor_matches": [
                        {
                            "vendor_id": "11111111-1111-1111-1111-111111111111",
                            "canonical_name": "Example",
                            "canonical_slug": "example",
                            "primary_domain": "example.com",
                            "match_reason": "Primary domain and canonical slug both matched.",
                            "confidence": 0.96,
                        }
                    ],
                    "product_matches": [
                        {
                            "product_id": "22222222-2222-2222-2222-222222222222",
                            "canonical_name": "Example Platform",
                            "canonical_slug": "example",
                            "vendor_id": "11111111-1111-1111-1111-111111111111",
                            "match_reason": "Product slug matched artifact slug within resolved vendor scope.",
                            "confidence": 0.88,
                        }
                    ],
                }
            },
        )()


def override_get_db():
    yield object()


def test_admin_entity_resolution_endpoint_returns_payload(monkeypatch) -> None:
    monkeypatch.setattr("apps.api.routes.admin_entity_resolution.EntityResolutionService", DummyEntityResolutionService)
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    response = client.post(
        "/v1/admin/entity-resolution/resolve",
        json={"vendor_domain": "example.com", "artifact_slug": "example"},
    )

    assert response.status_code == 200
    body = response.json()["data"]
    assert body["vendor_matches"][0]["canonical_slug"] == "example"
    assert body["product_matches"][0]["canonical_name"] == "Example Platform"

    app.dependency_overrides.clear()
