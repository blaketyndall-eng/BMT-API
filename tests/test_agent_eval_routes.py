from fastapi.testclient import TestClient

from apps.api.main import app
from packages.contracts.agent_evals import AgentEvalCheck, AgentEvalResponse, AgentEvalScorecard
from packages.core.deps import get_db


class DummyAgentEvaluatorService:
    def evaluate(self, payload):
        return AgentEvalResponse(
            agent_name=payload.agent_name,
            evaluator_version="agent_evaluator_v1",
            scorecard=AgentEvalScorecard(
                overall_passed=True,
                passed_checks=3,
                failed_checks=0,
                score=1.0,
            ),
            checks=[
                AgentEvalCheck(
                    check_name="has_proposals",
                    passed=True,
                    severity="medium",
                    message="ok",
                )
            ],
        )


def override_get_db():
    yield object()


def test_admin_agent_eval_endpoint_returns_payload(monkeypatch) -> None:
    monkeypatch.setattr("apps.api.routes.agent_evals.AgentEvaluatorService", lambda: DummyAgentEvaluatorService())
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    response = client.post(
        "/v1/admin/agent-evals/run",
        json={
            "agent_name": "source_planner_agent",
            "payload": {
                "proposals": [
                    {
                        "root_url": "https://docs.example.com",
                        "source_type": "docs_subdomain",
                        "reason": "Docs coverage is missing.",
                        "confidence": 0.9,
                    }
                ],
                "considered_gap_codes": ["missing_docs_surface"],
            },
        },
    )

    assert response.status_code == 200
    body = response.json()["data"]
    assert body["agent_name"] == "source_planner_agent"
    assert body["scorecard"]["overall_passed"] is True

    app.dependency_overrides.clear()
