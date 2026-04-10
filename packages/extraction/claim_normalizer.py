from __future__ import annotations

from dataclasses import dataclass

from packages.extraction.claim_taxonomy import get_claim_taxonomy_entry


@dataclass(frozen=True)
class NormalizedClaimKey:
    claim_type: str
    normalized_key: str
    display_label: str


def normalize_claim(*, claim_type: str, label: str) -> NormalizedClaimKey:
    entry = get_claim_taxonomy_entry(claim_type, label)
    return NormalizedClaimKey(
        claim_type=entry.claim_type,
        normalized_key=entry.normalized_key,
        display_label=entry.display_label,
    )
