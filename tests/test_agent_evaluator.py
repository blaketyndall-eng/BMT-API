from packages.contracts.agent_evals import AgentEvalRequest
from packages.services.agent_evaluator import AgentEvaluatorService


def test_evaluate_source_planner_payload_scores_expected_checks() -> None:
    service = AgentEvaluatorService()

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


def test_evaluate_evidence_critic_payload_flags_missing_recommendations() -> None:
    service = AgentEvaluatorService()

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
                    }
                ]
            },
        )
    )

    assert response.agent_name == "evidence_critic_agent"
    assert response.scorecard.failed_checks >= 1
    assert any(check.check_name == "recommendations_present" and not check.passed for check in response.checks)
