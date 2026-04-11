from fastapi.testclient import TestClient

from apps.api.main import app
from packages.contracts.source_registry import SourceRegistryEntry, SourceRegistryListResponse
from packages.core.deps import get_db


class DummySourceRegistryService:
    def __init__(self, _db: object) -> None:
        pass

    def list_registry_entries(self, **kwargs):
        return SourceRegistryListResponse(
            items=[
                SourceRegistryEntry(
                    source_id="11111111-1111-1111-1111-111111111111",
                    vendor_id=None,
                    product_id="00000000-0000-0000-0000-000000000001",
                    root_url="https://docs.example.com",
                    source_family="vendor_owned",
                    source_group="developer_shipped_truth",
                    source_type="docs_subdomain",
                    policy_zone="green",
                    connector_type="browser",
                    machine_readable=False,
                    crawler_mode="browser_fetch",
                    parser_chain=["docs_nav_parser", "html_claim_extractor"],
                    base_confidence_weight=0.92,
                    freshness_profile="medium_volatility",
                    refresh_cadence="weekly",
                    provenance_required=True,
                    terms_review_required=False,
                    notes=None,
                )
            ]
        )


def override_get_db():
    yield object()


def test_admin_source_registry_endpoint_returns_payload(monkeypatch) -> None:
    monkeypatch.setattr("apps.api.routes.admin_source_registry.SourceRegistryService", DummySourceRegistryService)
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    response = client.get("/v1/admin/source-registry?source_group=developer_shipped_truth&limit=10")

    assert response.status_code == 200
    body = response.json()["data"]
    assert body["items"][0]["source_group"] == "developer_shipped_truth"
    assert body["items"][0]["parser_chain"][0] == "docs_nav_parser"

    app.dependency_overrides.clear()
