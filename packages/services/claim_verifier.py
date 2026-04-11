from __future__ import annotations

from packages.contracts.agent_evals import ClaimVerificationItem, ClaimVerificationSummary

_SUPPORTED_BUCKETS = {"backed", "thin", "unsupported", "stale_supported"}


class ClaimVerifierService:
    def classify_evidence_critic_payload(self, payload: dict) -> ClaimVerificationSummary:
        critiques = payload.get("critiques") or []
        items: list[ClaimVerificationItem] = []

        for critique in critiques:
            support_quality = critique.get("support_quality")
            confidence = float(critique.get("confidence", 0.0))
            reason = critique.get("reason") or ""

            if support_quality == "strong":
                bucket = "backed"
            elif support_quality == "thin":
                bucket = "thin"
            elif support_quality == "weak":
                if "stale" in reason.lower():
                    bucket = "stale_supported"
                else:
                    bucket = "unsupported"
            else:
                bucket = "unsupported"

            if bucket not in _SUPPORTED_BUCKETS:
                bucket = "unsupported"

            items.append(
                ClaimVerificationItem(
                    claim_id=str(critique.get("claim_id")),
                    normalized_key=str(critique.get("normalized_key")),
                    bucket=bucket,
                    confidence=confidence,
                )
            )

        return ClaimVerificationSummary(
            backed_claim_count=len([item for item in items if item.bucket == "backed"]),
            thin_claim_count=len([item for item in items if item.bucket == "thin"]),
            unsupported_claim_count=len([item for item in items if item.bucket == "unsupported"]),
            stale_supported_claim_count=len([item for item in items if item.bucket == "stale_supported"]),
            items=items,
        )
