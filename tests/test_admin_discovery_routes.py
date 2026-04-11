from fastapi.testclient import TestClient

from apps.api.main import app
from packages.core.deps import get_db


class DummyRegistryManagerService:
    def __init__(self, _db: object) -> None:
        pass

    def run_discovery(self, payload):
        return type(
            "Resp",
            (),
            {
                "model_dump": lambda self: {
                    "vendor_domain": payload.vendor_domain,
                    "discovery_groups_run": ["surface_mapper", "machine_readable_finder", "ecosystem_finder"],
                    "candidates": [
                        {
                            "root_url": "https://docs.example.com",
                            "source_family": "vendor_owned",
                            "source_type": "docs_subdomain",
                            "source_group": "developer_shipped_truth",
                            "policy_zone": "green",
                            "connector_type": "browser",
                            "machine_readable": False,
                            "crawler_mode": "browser_fetch",
                            "parser_chain": ["docs_nav_parser", "html_claim_extractor"],
                            "base_confidence_weight": 0.92,
                            "provenance_required": True,
                            "terms_review_required": False,
                            "notes": "Docs subdomain if present.",
                        },
                        {
                            "root_url": "https://github.com/example",
                            "source_family": "repo",
                            "source_type": "official_repo_org",
                            "source_group": "ecosystem_commercial",
                            "policy_zone": "green",
                            "connector_type": "api",
                            "machine_readable": False,
                            "crawler_mode": "repo_api",
                            "parser_chain": ["repo_metadata_parser"],
                            "base_confidence_weight": 0.84,
                            "provenance_required": True,
                            "terms_review_required": False,
                            "notes": "Likely public source-control organization if it exists.",
                        }
                    ],
                }
            },
        )()


def override_get_db():
    yield object()


def test_admin_discovery_run_returns_candidates_and_groups(monkeypatch) -> None:
    monkeypatch.setattr("apps.api.routes.admin_discovery.RegistryManagerService", DummyRegistryManagerService)
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    response = client.post(
        "/v1/admin/discovery/run",
        json={"vendor_domain": "example.com", "include_machine_readable": True, "include_ecosystem": True},
    )

    assert response.status_code == 200
    body = response.json()["data"]
    assert body["vendor_domain"] == "example.com"
    assert body["discovery_groups_run"] == ["surface_mapper", "machine_readable_finder", "ecosystem_finder"]
    assert body["candidates"][1]["source_group"] == "ecosystem_commercial"
    assert body["candidates"][1]["root_url"] == "https://github.com/example"

    app.dependency_overrides.clear()
