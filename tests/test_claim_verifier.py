from packages.services.claim_verifier import ClaimVerifierService


def test_classify_evidence_critic_payload_counts_claim_buckets() -> None:
    service = ClaimVerifierService()

    summary = service.classify_evidence_critic_payload(
        {
            "critiques": [
                {
                    "claim_id": "capability:sso",
                    "normalized_key": "single_sign_on",
                    "support_quality": "strong",
                    "confidence": 0.91,
                    "reason": "Docs-backed and supported by multiple sources.",
                },
                {
                    "claim_id": "capability:slack",
                    "normalized_key": "slack",
                    "support_quality": "thin",
                    "confidence": 0.74,
                    "reason": "Only one source supports this claim.",
                },
                {
                    "claim_id": "capability:api",
                    "normalized_key": "api_access",
                    "support_quality": "weak",
                    "confidence": 0.41,
                    "reason": "Claim support is stale.",
                },
                {
                    "claim_id": "capability:bad",
                    "normalized_key": "unknown",
                    "support_quality": "weak",
                    "confidence": 0.2,
                    "reason": "No evidence excerpts were returned.",
                },
            ]
        }
    )

    assert summary.backed_claim_count == 1
    assert summary.thin_claim_count == 1
    assert summary.stale_supported_claim_count == 1
    assert summary.unsupported_claim_count == 1
    assert len(summary.items) == 4
