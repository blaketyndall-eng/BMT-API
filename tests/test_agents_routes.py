from fastapi.testclient import TestClient

from apps.api.main import app
from packages.contracts.agents import AgentRunSummary, SourcePlannerResponse, SourceProposal
from packages.core.deps import get_db


class DummySourcePlannerAgentService:
    def __init__(self, _db: object) -> None:
        pass

    def plan(self, request):
        return SourcePlannerResponse(
            product_id=request.product_id,
            agent=AgentRunSummary(
                agent_name="source_planner_agent",
                strategy_version="source_planner_v1",
                mode="heuristic_scaffold",
            ),
            considered_gap_codes=["missing_docs_surface"],
            proposals=[
                SourceProposal(
                    root_url="https://docs.example.com",
                    source_type="docs_subdomain",
                    reason="Docs coverage is missing.",
                    target_gap_codes=["missing_docs_surface"],
                    confidence=0.9,
                )
            ],
        )


def override_get_db():
    yield object()


def test_source_planner_agent_endpoint_returns_payload(monkeypatch) -> None:
    monkeypatch.setattr("apps.api.routes.agents.SourcePlannerAgentService", DummySourcePlannerAgentService)
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    response = client.post(
        "/v1/agents/source-planner/plan",
        json={"product_id": "00000000-0000-0000-0000-000000000001", "max_candidates": 5},
    )

    assert response.status_code == 200
    body = response.json()["data"]
    assert body["agent"]["agent_name"] == "source_planner_agent"
    assert body["proposals"][0]["root_url"] == "https://docs.example.com"
    assert body["considered_gap_codes"] == ["missing_docs_surface"]

    app.dependency_overrides.clear()
