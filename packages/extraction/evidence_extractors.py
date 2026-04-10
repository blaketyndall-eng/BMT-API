from __future__ import annotations

import re
from dataclasses import dataclass

EXTRACTOR_NAME = "page_evidence_extractor"
EXTRACTOR_VERSION = "evidence_v1"
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")

CAPABILITY_KEYWORDS: dict[str, tuple[str, ...]] = {
    "single_sign_on": ("single sign-on", "single sign on", "sso"),
    "scim_provisioning": ("scim", "provisioning"),
    "audit_logs": ("audit log", "audit logs"),
    "webhooks": ("webhook", "webhooks"),
    "api_access": ("api access", "rest api", "graphql api"),
    "workflow_automation": ("workflow", "workflow automation", "approval workflow"),
    "analytics_reporting": ("analytics", "reporting", "reports"),
    "dashboards": ("dashboard", "dashboards"),
    "search": ("search", "semantic search", "global search"),
    "templates": ("template", "templates"),
    "notifications": ("notification", "notifications"),
    "role_based_access_control": ("rbac", "role-based access control", "permissions"),
    "exports": ("export", "exports", "csv export"),
}

INTEGRATION_KEYWORDS: dict[str, tuple[str, ...]] = {
    "salesforce": ("salesforce",),
    "slack": ("slack",),
    "jira": ("jira",),
    "hubspot": ("hubspot",),
    "microsoft_teams": ("microsoft teams", "teams"),
    "google_drive": ("google drive",),
    "sharepoint": ("sharepoint",),
    "box": ("box",),
    "okta": ("okta",),
    "azure_ad": ("azure ad", "microsoft entra", "entra id"),
    "zapier": ("zapier",),
    "github": ("github",),
}

CHANGE_HINTS = ("added", "new", "improved", "support", "supported", "fixed", "introduced", "launch")


@dataclass(frozen=True)
class ExtractedEvidence:
    evidence_type: str
    label: str
    snippet: str
    confidence: float
    metadata: dict[str, str | float]


def _sentences(page_text: str | None) -> list[str]:
    if not page_text:
        return []
    parts = [part.strip() for part in SENTENCE_SPLIT_RE.split(page_text) if part.strip()]
    return [part[:500] for part in parts if len(part) > 20]


def _extract_keyword_evidence(
    *,
    evidence_type: str,
    keywords: dict[str, tuple[str, ...]],
    sentences: list[str],
    confidence: float,
) -> list[ExtractedEvidence]:
    found: list[ExtractedEvidence] = []
    seen_labels: set[str] = set()

    for sentence in sentences:
        sentence_l = sentence.lower()
        for label, variants in keywords.items():
            if label in seen_labels:
                continue
            if any(variant in sentence_l for variant in variants):
                found.append(
                    ExtractedEvidence(
                        evidence_type=evidence_type,
                        label=label,
                        snippet=sentence,
                        confidence=confidence,
                        metadata={"match_type": "keyword_sentence"},
                    )
                )
                seen_labels.add(label)

    return found


def extract_page_evidence(*, page_type: str | None, title: str | None, page_text: str | None) -> list[ExtractedEvidence]:
    sentences = _sentences(page_text)
    results: list[ExtractedEvidence] = []

    if page_type in {"docs", "api_reference", "homepage", "generic", None}:
        results.extend(
            _extract_keyword_evidence(
                evidence_type="capability",
                keywords=CAPABILITY_KEYWORDS,
                sentences=sentences,
                confidence=0.74 if page_type in {"docs", "api_reference"} else 0.62,
            )
        )
        results.extend(
            _extract_keyword_evidence(
                evidence_type="integration",
                keywords=INTEGRATION_KEYWORDS,
                sentences=sentences,
                confidence=0.78 if page_type in {"docs", "api_reference"} else 0.66,
            )
        )

    if page_type == "changelog":
        seen_change_snippets: set[str] = set()
        for sentence in sentences:
            sentence_l = sentence.lower()
            if not any(hint in sentence_l for hint in CHANGE_HINTS):
                continue
            normalized = sentence.strip()
            if normalized in seen_change_snippets:
                continue
            seen_change_snippets.add(normalized)
            label = " ".join(normalized.split()[:8]).lower()
            results.append(
                ExtractedEvidence(
                    evidence_type="change_event",
                    label=label[:255],
                    snippet=normalized,
                    confidence=0.81,
                    metadata={"match_type": "changelog_sentence", "title": title or ""},
                )
            )
            if len(seen_change_snippets) >= 10:
                break

    return results
