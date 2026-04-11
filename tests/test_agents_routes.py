from fastapi.testclient import TestClient

from apps.api.main import app
from packages.contracts.agents import (
    AgentRunSummary,
    EvidenceCriticResponse,
    EvidenceCritiqueItem,
    SourcePlannerResponse,
    SourceProposal,
)
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


class DummyEvidenceCriticAgentService:
    def __init__(self, _db: object) -> None:
        pass

    def critique(self, request):
        return EvidenceCriticResponse(
            product_id=request.product_id,
            agent=AgentRunSummary(
                agent_name="evidence_critic_agent",
                strategy_version="evidence_critic_v1",
                mode="heuristic_scaffold",
            ),
            critiques=[
                EvidenceCritiqueItem(
                    claim_id="capability:single_sign_on",
                    claim_type="capability",
                    normalized_key="single_sign_on",
                    display_label="Single Sign-On",
                    support_quality="thin",
                    confidence=0.82,
                    reason="Claim is supported by only one source.",
                    recommendations=["Find a second confirming source, ideally docs or API reference."],
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


def test_evidence_critic_agent_endpoint_returns_payload(monkeypatch) -> None:
    monkeypatch.setattr("apps.api.routes.agents.EvidenceCriticAgentService", DummyEvidenceCriticAgentService)
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    response = client.post(
        "/v1/agents/evidence-critic/critique",
        json={"product_id": "00000000-0000-0000-0000-000000000001", "min_confidence": 0.6, "limit": 5},
    )

    assert response.status_code == 200
    body = response.json()["data"]
    assert body["agent"]["agent_name"] == "evidence_critic_agent"
    assert body["critiques"][0]["support_quality"] == "thin"
    assert body["critiques"][0]["normalized_key"] == "single_sign_on"

    app.dependency_overrides.clear()
