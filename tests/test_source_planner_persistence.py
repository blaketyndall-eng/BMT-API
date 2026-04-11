from packages.contracts.agents import SourcePlannerRequest
from packages.contracts.product_intelligence import GapItem
from packages.services.source_planner_agent import SourcePlannerAgentService


class DummyProductIntelligence:
    def _get_claim_rows(self, product_id):
        return []

    def _get_page_types(self, product_id):
        return {"homepage"}


class DummyStore:
    def __init__(self):
        self.calls = []

    def create_agent_run(self, **kwargs):
        self.calls.append(kwargs)
        return object()


class DummySession:
    def commit(self):
        return None


def test_source_planner_persists_agent_run(monkeypatch) -> None:
    service = SourcePlannerAgentService(DummySession())  # type: ignore[arg-type]
    service.product_intelligence = DummyProductIntelligence()
    service.agent_run_store = DummyStore()

    monkeypatch.setattr(
        service,
        "_get_product_vendor_context",
        lambda product_id: {"product_name": "Example", "primary_domain": "example.com", "vendor_id": None},
    )
    monkeypatch.setattr(service, "_get_existing_sources", lambda product_id: set())
    monkeypatch.setattr(
        "packages.services.source_planner_agent.detect_product_gaps",
        lambda page_types, claims: [
            GapItem(
                gap_code="missing_docs_surface",
                category="docs",
                severity="high",
                message="Missing docs.",
                evidence_count=0,
                suggested_source_types=["docs_subdomain"],
            )
        ],
    )

    response = service.plan(
        SourcePlannerRequest(product_id="00000000-0000-0000-0000-000000000001", max_candidates=3)
    )

    assert response.agent.agent_name == "source_planner_agent"
    assert len(service.agent_run_store.calls) == 1
    assert service.agent_run_store.calls[0]["agent_name"] == "source_planner_agent"
