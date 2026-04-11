from __future__ import annotations

from dataclasses import dataclass

from packages.contracts.agents import SourceProposal

_SOURCE_TYPE_PRIORS = {
    "pricing": 0.2,
    "docs_subdomain": 0.18,
    "docs_path": 0.12,
    "developers_subdomain": 0.11,
    "changelog": 0.16,
    "release_notes": 0.12,
    "integrations_directory": 0.15,
    "homepage": 0.04,
}


@dataclass
class ProposalHistory:
    promoted_count: int = 0
    rejected_count: int = 0
    same_type_existing_count: int = 0
    recent_failed_crawls: int = 0


class SourcePlannerRanker:
    def score(self, proposal: SourceProposal, history: ProposalHistory) -> float:
        score = proposal.confidence
        score += _SOURCE_TYPE_PRIORS.get(proposal.source_type, 0.0)
        score += min(history.promoted_count * 0.08, 0.24)
        score -= min(history.rejected_count * 0.12, 0.36)
        score -= min(history.same_type_existing_count * 0.05, 0.2)
        score -= min(history.recent_failed_crawls * 0.1, 0.3)
        return round(score, 4)

    def rank(
        self,
        proposals: list[SourceProposal],
        history_by_url: dict[str, ProposalHistory],
    ) -> list[SourceProposal]:
        scored: list[tuple[float, SourceProposal]] = []
        for proposal in proposals:
            history = history_by_url.get(proposal.root_url, ProposalHistory())
            score = self.score(proposal, history)
            reason_suffix = self._reason_suffix(history)
            proposal_with_reason = proposal.model_copy(update={
                "reason": proposal.reason + reason_suffix,
                "confidence": min(max(round(score, 3), 0.0), 1.0),
            })
            scored.append((score, proposal_with_reason))

        scored.sort(key=lambda item: item[0], reverse=True)
        return [proposal for _, proposal in scored]

    def _reason_suffix(self, history: ProposalHistory) -> str:
        parts: list[str] = []
        if history.promoted_count > 0 and history.rejected_count == 0:
            parts.append("similar proposals were previously promoted")
        elif history.rejected_count > 0 and history.promoted_count == 0:
            parts.append("similar proposals were previously rejected")
        elif history.promoted_count > 0 and history.rejected_count > 0:
            parts.append("prior promotion and rejection outcomes are mixed")

        if history.same_type_existing_count > 0:
            parts.append("this source type already has existing coverage")
        if history.recent_failed_crawls > 0:
            parts.append("similar recent crawl attempts failed")

        if not parts:
            return " Ranked using source-type prior and current evidence-gap fit."
        return " Ranking considers that " + "; ".join(parts) + "."
