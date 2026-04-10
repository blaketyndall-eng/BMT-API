from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse

CLASSIFIER_VERSION = "page_classifier_v1"


@dataclass(frozen=True)
class PageClassification:
    page_type: str
    confidence: float
    reasons: list[str]


def classify_page(
    *,
    requested_url: str,
    final_url: str,
    title: str | None,
    page_text: str | None,
    source_type: str | None,
) -> PageClassification:
    parsed = urlparse(final_url or requested_url)
    host = (parsed.netloc or "").lower()
    path = (parsed.path or "/").lower()
    title_l = (title or "").lower()
    text = (page_text or "").lower()

    def result(page_type: str, confidence: float, *reasons: str) -> PageClassification:
        return PageClassification(page_type=page_type, confidence=confidence, reasons=list(reasons))

    if host.startswith("status.") or "/status" in path or any(token in title_l for token in ["status", "uptime", "incidents"]):
        return result("status", 0.99, "status url/title pattern")

    if any(token in path for token in ["/changelog", "/release-notes", "/releases", "/whats-new"]) or any(
        token in title_l for token in ["changelog", "release notes", "what's new", "whats new"]
    ):
        return result("changelog", 0.97, "changelog url/title pattern")

    if any(token in path for token in ["/api", "/reference", "/openapi", "/swagger", "/redoc", "/graphql"]) or any(
        token in title_l for token in ["api reference", "api docs", "developer documentation", "graphql"]
    ):
        return result("api_reference", 0.96, "api/reference url/title pattern")

    if host.startswith("docs.") or host.startswith("developers.") or any(
        token in path for token in ["/docs", "/documentation", "/guides", "/guide", "/learn"]
    ) or any(token in title_l for token in ["docs", "documentation", "developer docs"]):
        return result("docs", 0.93, "docs url/title pattern")

    if any(token in path for token in ["/pricing", "/plans", "/plan"]) or any(
        token in title_l for token in ["pricing", "plans", "plan & pricing"]
    ) or any(token in text for token in ["request a demo", "contact sales", "pricing", "per month"]):
        return result("pricing", 0.95, "pricing url/title/text pattern")

    if source_type == "status":
        return result("status", 0.9, "source type fallback")
    if source_type in {"changelog", "release_notes"}:
        return result("changelog", 0.88, "source type fallback")
    if source_type == "api_reference":
        return result("api_reference", 0.88, "source type fallback")
    if source_type in {"docs_subdomain", "developers_subdomain", "docs_path"}:
        return result("docs", 0.85, "source type fallback")
    if source_type == "pricing":
        return result("pricing", 0.85, "source type fallback")

    if path in {"", "/"}:
        return result("homepage", 0.8, "root path fallback")

    return result("generic", 0.55, "generic fallback")
