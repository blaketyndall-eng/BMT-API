from __future__ import annotations

from packages.contracts.agent_evals import (
    AgentEvalCheck,
    AgentEvalRequest,
    AgentEvalResponse,
    AgentEvalScorecard,
)
from packages.observability.tracing import log_event, traced_span

EVALUATOR_VERSION = "agent_evaluator_v1"
_ALLOWED_SUPPORT_QUALITIES = {"strong", "thin", "weak"}


class AgentEvaluatorService:
    def evaluate(self, request: AgentEvalRequest) -> AgentEvalResponse:
        with traced_span("agent_evaluator.evaluate", agent_name=request.agent_name):
            if request.agent_name == "source_planner_agent":
                checks = self._evaluate_source_planner_payload(request.payload)
            elif request.agent_name == "evidence_critic_agent":
                checks = self._evaluate_evidence_critic_payload(request.payload)
            else:
                checks = [
                    AgentEvalCheck(
                        check_name="known_agent",
                        passed=False,
                        severity="high",
                        message=f"No evaluator is registered for agent '{request.agent_name}'.",
                    )
                ]

            failed_checks = len([check for check in checks if not check.passed])
            passed_checks = len(checks) - failed_checks
            overall_passed = failed_checks == 0
            score = round(passed_checks / len(checks), 3) if checks else 0.0
            log_event(
                "agent_evaluator.completed",
                agent_name=request.agent_name,
                passed_checks=passed_checks,
                failed_checks=failed_checks,
                score=score,
            )
            return AgentEvalResponse(
                agent_name=request.agent_name,
                evaluator_version=EVALUATOR_VERSION,
                scorecard=AgentEvalScorecard(
                    overall_passed=overall_passed,
                    passed_checks=passed_checks,
                    failed_checks=failed_checks,
                    score=score,
                ),
                checks=checks,
            )

    def _evaluate_source_planner_payload(self, payload: dict) -> list[AgentEvalCheck]:
        proposals = payload.get("proposals") or []
        considered_gap_codes = payload.get("considered_gap_codes") or []

        checks = [
            AgentEvalCheck(
                check_name="has_proposals",
                passed=len(proposals) > 0,
                severity="medium",
                message="Source planner should usually return at least one proposal.",
            ),
            AgentEvalCheck(
                check_name="proposal_reasons_present",
                passed=all(bool(proposal.get("reason")) for proposal in proposals),
                severity="medium",
                message="Every proposal should include a human-readable reason.",
            ),
            AgentEvalCheck(
                check_name="proposal_confidence_in_range",
                passed=all(0.0 <= float(proposal.get("confidence", -1)) <= 1.0 for proposal in proposals),
                severity="high",
                message="Every proposal confidence should be between 0.0 and 1.0.",
            ),
            AgentEvalCheck(
                check_name="proposal_urls_unique",
                passed=len({proposal.get("root_url") for proposal in proposals}) == len(proposals),
                severity="medium",
                message="Proposals should not contain duplicate root URLs.",
            ),
            AgentEvalCheck(
                check_name="gap_coverage_present",
                passed=len(considered_gap_codes) > 0,
                severity="low",
                message="Source planner output should disclose the gap codes it considered.",
            ),
        ]
        return checks

    def _evaluate_evidence_critic_payload(self, payload: dict) -> list[AgentEvalCheck]:
        critiques = payload.get("critiques") or []

        checks = [
            AgentEvalCheck(
                check_name="has_critiques",
                passed=len(critiques) > 0,
                severity="medium",
                message="Evidence critic should usually return at least one critique item.",
            ),
            AgentEvalCheck(
                check_name="support_quality_valid",
                passed=all(critique.get("support_quality") in _ALLOWED_SUPPORT_QUALITIES for critique in critiques),
                severity="high",
                message="Support quality should be one of strong, thin, or weak.",
            ),
            AgentEvalCheck(
                check_name="reasons_present",
                passed=all(bool(critique.get("reason")) for critique in critiques),
                severity="medium",
                message="Every critique should include a reason.",
            ),
            AgentEvalCheck(
                check_name="recommendations_present",
                passed=all(len(critique.get("recommendations") or []) > 0 for critique in critiques),
                severity="low",
                message="Every critique should include at least one recommendation.",
            ),
            AgentEvalCheck(
                check_name="confidence_in_range",
                passed=all(0.0 <= float(critique.get("confidence", -1)) <= 1.0 for critique in critiques),
                severity="high",
                message="Every critique confidence should be between 0.0 and 1.0.",
            ),
        ]
        return checks
