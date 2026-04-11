from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from packages.contracts.agents import (
    AgentRunSummary,
    EvidenceCriticRequest,
    EvidenceCriticResponse,
    EvidenceCritiqueItem,
)
from packages.observability.tracing import log_event, traced_span
from packages.services.product_intelligence import ProductIntelligenceService

STRATEGY_VERSION = "evidence_critic_v1"


class EvidenceCriticAgentService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.product_intelligence = ProductIntelligenceService(db)

    def critique(self, request: EvidenceCriticRequest) -> EvidenceCriticResponse:
        product_id = uuid.UUID(request.product_id)
        with traced_span("agent.evidence_critic.critique", product_id=request.product_id):
            claims_response = self.product_intelligence.get_product_claims(
                product_id,
                min_confidence=request.min_confidence,
                include_stale=True,
                include_evidence=True,
            )
            critiques = [self._critique_claim(claim) for claim in claims_response.items[: request.limit]]
            log_event(
                "agent.evidence_critic.completed",
                product_id=request.product_id,
                critique_count=len(critiques),
            )
            return EvidenceCriticResponse(
                product_id=request.product_id,
                agent=AgentRunSummary(
                    agent_name="evidence_critic_agent",
                    strategy_version=STRATEGY_VERSION,
                    mode="heuristic_scaffold",
                ),
                critiques=critiques,
            )

    def _critique_claim(self, claim) -> EvidenceCritiqueItem:
        support_quality = "strong"
        reason_parts: list[str] = []
        recommendations: list[str] = []

        if "stale" in claim.flags:
            support_quality = "weak"
            reason_parts.append("Claim support is stale.")
            recommendations.append("Recrawl the primary source and changelog surfaces.")
        if claim.source_count <= 1:
            support_quality = "thin"
            reason_parts.append("Claim is supported by only one source.")
            recommendations.append("Find a second confirming source, ideally docs or API reference.")
        if not claim.evidence:
            support_quality = "weak"
            reason_parts.append("No evidence excerpts were returned in the current payload.")
            recommendations.append("Request the claim with include_evidence enabled for manual review.")
        if "docs_backed" in claim.flags and claim.source_count > 1 and "stale" not in claim.flags:
            reason_parts.append("Claim is backed by docs-like evidence and multiple sources.")
            if support_quality == "strong":
                recommendations.append("No immediate action needed.")

        if not reason_parts:
            reason_parts.append("Claim support is adequate but should still be periodically refreshed.")
            recommendations.append("Monitor for freshness drift.")

        return EvidenceCritiqueItem(
            claim_id=claim.claim_id,
            claim_type=claim.claim_type,
            normalized_key=claim.normalized_key,
            display_label=claim.display_label,
            support_quality=support_quality,
            confidence=claim.confidence,
            reason=" ".join(reason_parts),
            recommendations=recommendations,
        )
