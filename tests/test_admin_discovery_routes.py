from fastapi.testclient import TestClient

from apps.api.main import app


class DummyDiscoveryService:
    def discover(self, payload):
        return type(
            "Resp",
            (),
            {
                "model_dump": lambda self: {
                    "vendor_domain": payload.vendor_domain,
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
                        }
                    ],
                }
            },
        )()


def test_admin_discovery_run_returns_candidates(monkeypatch) -> None:
    monkeypatch.setattr("apps.api.routes.admin_discovery.DiscoveryService", DummyDiscoveryService)
    client = TestClient(app)

    response = client.post(
        "/v1/admin/discovery/run",
        json={"vendor_domain": "example.com", "include_machine_readable": True},
    )

    assert response.status_code == 200
    body = response.json()["data"]
    assert body["vendor_domain"] == "example.com"
    assert body["candidates"][0]["source_group"] == "developer_shipped_truth"
    assert body["candidates"][0]["root_url"] == "https://docs.example.com"
