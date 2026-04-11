from datetime import datetime, timezone

from fastapi.testclient import TestClient

from apps.api.main import app
from packages.contracts.admin import (
    AgentEvalRunListResponse,
    AgentEvalRunSummary,
    AgentRunListResponse,
    AgentRunSummary,
    SourceProposalDecisionListResponse,
    SourceProposalDecisionSummary,
)
from packages.core.deps import get_db


class DummyAdminQueryService:
    def __init__(self, _db: object) -> None:
        pass

    def list_agent_runs(self, **kwargs):
        now = datetime.now(timezone.utc)
        return AgentRunListResponse(
            items=[
                AgentRunSummary(
                    agent_run_id="11111111-1111-1111-1111-111111111111",
                    agent_name="source_planner_agent",
                    strategy_version="source_planner_v1",
                    mode="heuristic_scaffold",
                    status="completed",
                    trace_id="trace-1",
                    request_id="request-1",
                    product_id="00000000-0000-0000-0000-000000000001",
                    vendor_id=None,
                    created_at=now,
                    updated_at=now,
                )
            ]
        )

    def list_agent_eval_runs(self, **kwargs):
        now = datetime.now(timezone.utc)
        return AgentEvalRunListResponse(
            items=[
                AgentEvalRunSummary(
                    agent_eval_run_id="22222222-2222-2222-2222-222222222222",
                    agent_name="source_planner_agent",
                    evaluator_version="agent_evaluator_v1",
                    status="completed",
                    trace_id="trace-1",
                    score=1.0,
                    overall_passed=True,
                    created_at=now,
                    updated_at=now,
                )
            ]
        )

    def list_source_proposal_decisions(self, **kwargs):
        now = datetime.now(timezone.utc)
        return SourceProposalDecisionListResponse(
            items=[
                SourceProposalDecisionSummary(
                    source_proposal_decision_id="33333333-3333-3333-3333-333333333333",
                    decision_type="promote",
                    agent_name="source_planner_agent",
                    trace_id="trace-1",
                    product_id="00000000-0000-0000-0000-000000000001",
                    vendor_id=None,
                    source_id="44444444-4444-4444-4444-444444444444",
                    crawl_job_id="55555555-5555-5555-5555-555555555555",
                    proposal_root_url="https://docs.example.com",
                    note=None,
                    created_at=now,
                    updated_at=now,
                )
            ]
        )


def override_get_db():
    yield object()


def test_admin_agent_runs_endpoint_returns_payload(monkeypatch) -> None:
    monkeypatch.setattr("apps.api.routes.admin_agent_ops.AdminQueryService", DummyAdminQueryService)
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    response = client.get("/v1/admin/agent-runs?agent_name=source_planner_agent&limit=10")

    assert response.status_code == 200
    body = response.json()["data"]
    assert body["items"][0]["agent_name"] == "source_planner_agent"
    assert body["items"][0]["trace_id"] == "trace-1"

    app.dependency_overrides.clear()


def test_admin_agent_evals_endpoint_returns_payload(monkeypatch) -> None:
    monkeypatch.setattr("apps.api.routes.admin_agent_ops.AdminQueryService", DummyAdminQueryService)
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    response = client.get("/v1/admin/agent-evals?agent_name=source_planner_agent&limit=10")

    assert response.status_code == 200
    body = response.json()["data"]
    assert body["items"][0]["evaluator_version"] == "agent_evaluator_v1"
    assert body["items"][0]["overall_passed"] is True

    app.dependency_overrides.clear()


def test_admin_source_proposal_decisions_endpoint_returns_payload(monkeypatch) -> None:
    monkeypatch.setattr("apps.api.routes.admin_agent_ops.AdminQueryService", DummyAdminQueryService)
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    response = client.get("/v1/admin/source-proposal-decisions?decision_type=promote&limit=10")

    assert response.status_code == 200
    body = response.json()["data"]
    assert body["items"][0]["decision_type"] == "promote"
    assert body["items"][0]["proposal_root_url"] == "https://docs.example.com"

    app.dependency_overrides.clear()
