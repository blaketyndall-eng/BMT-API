from packages.contracts.agent_evals import AgentEvalRequest
from packages.services.agent_evaluator import AgentEvaluatorService


class DummyStore:
    def __init__(self):
        self.calls = []

    def create_agent_eval_run(self, **kwargs):
        self.calls.append(kwargs)
        return object()


class DummySession:
    def commit(self):
        return None


def test_evaluate_source_planner_payload_scores_expected_checks() -> None:
    service = AgentEvaluatorService(DummySession())  # type: ignore[arg-type]
    service.agent_run_store = DummyStore()

    response = service.evaluate(
        AgentEvalRequest(
            agent_name="source_planner_agent",
            payload={
                "considered_gap_codes": ["missing_docs_surface"],
                "proposals": [
                    {
                        "root_url": "https://docs.example.com",
                        "source_type": "docs_subdomain",
                        "reason": "Docs coverage is missing.",
                        "confidence": 0.9,
                    }
                ],
            },
        )
    )

    assert response.agent_name == "source_planner_agent"
    assert response.scorecard.failed_checks == 0
    assert response.scorecard.overall_passed is True
    assert response.claim_verification is None
    assert len(service.agent_run_store.calls) == 1


def test_evaluate_evidence_critic_payload_flags_missing_recommendations_and_returns_claim_verification() -> None:
    service = AgentEvaluatorService(DummySession())  # type: ignore[arg-type]
    service.agent_run_store = DummyStore()

    response = service.evaluate(
        AgentEvalRequest(
            agent_name="evidence_critic_agent",
            payload={
                "critiques": [
                    {
                        "claim_id": "capability:single_sign_on",
                        "claim_type": "capability",
                        "normalized_key": "single_sign_on",
                        "display_label": "Single Sign-On",
                        "support_quality": "thin",
                        "confidence": 0.82,
                        "reason": "Only one source supports this claim.",
                        "recommendations": [],
                    },
                    {
                        "claim_id": "capability:api_access",
                        "claim_type": "capability",
                        "normalized_key": "api_access",
                        "display_label": "API Access",
                        "support_quality": "weak",
                        "confidence": 0.41,
                        "reason": "Claim support is stale.",
                        "recommendations": ["Recrawl the primary source and changelog surfaces."],
                    },
                ]
            },
        )
    )

    assert response.agent_name == "evidence_critic_agent"
    assert response.scorecard.failed_checks >= 1
    assert len(service.agent_run_store.calls) == 1
    assert response.claim_verification is not None
    assert response.claim_verification.thin_claim_count == 1
    assert response.claim_verification.stale_supported_claim_count == 1
    assert any(check.check_name == "recommendations_present" and not check.passed for check in response.checks)
