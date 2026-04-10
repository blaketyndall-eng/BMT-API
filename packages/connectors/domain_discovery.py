from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass(frozen=True)
class DiscoveredSourceCandidate:
    source_family: str
    source_type: str
    root_url: str
    connector_type: str
    metadata: dict[str, str]


def normalize_domain(value: str) -> str:
    candidate = value.strip().lower()
    if "://" not in candidate:
        candidate = f"https://{candidate}"

    parsed = urlparse(candidate)
    host = parsed.netloc or parsed.path
    host = host.split("/")[0]
    host = host.split(":")[0]
    if host.startswith("www."):
        host = host[4:]

    return host


def slugify_name(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "vendor"


def infer_vendor_name(domain: str) -> str:
    first_label = domain.split(".")[0]
    tokens = [token for token in re.split(r"[-_]+", first_label) if token]
    if not tokens:
        return "Vendor"
    return " ".join(token.capitalize() for token in tokens)


def build_candidate_sources(domain: str) -> list[DiscoveredSourceCandidate]:
    base_url = f"https://{domain}"
    candidates = [
        DiscoveredSourceCandidate("vendor_owned", "homepage", base_url, "browser", {"discovery_method": "inference"}),
        DiscoveredSourceCandidate("vendor_owned", "docs_subdomain", f"https://docs.{domain}", "browser", {"discovery_method": "inference"}),
        DiscoveredSourceCandidate("vendor_owned", "developers_subdomain", f"https://developers.{domain}", "browser", {"discovery_method": "inference"}),
        DiscoveredSourceCandidate("vendor_owned", "docs_path", f"{base_url}/docs", "browser", {"discovery_method": "inference"}),
        DiscoveredSourceCandidate("vendor_owned", "api_reference", f"{base_url}/api", "browser", {"discovery_method": "inference"}),
        DiscoveredSourceCandidate("vendor_owned", "changelog", f"{base_url}/changelog", "browser", {"discovery_method": "inference"}),
        DiscoveredSourceCandidate("vendor_owned", "release_notes", f"{base_url}/release-notes", "browser", {"discovery_method": "inference"}),
        DiscoveredSourceCandidate("vendor_owned", "pricing", f"{base_url}/pricing", "browser", {"discovery_method": "inference"}),
        DiscoveredSourceCandidate("vendor_owned", "status", f"https://status.{domain}", "browser", {"discovery_method": "inference"}),
    ]

    deduped: list[DiscoveredSourceCandidate] = []
    seen_urls: set[str] = set()
    for candidate in candidates:
        if candidate.root_url in seen_urls:
            continue
        deduped.append(candidate)
        seen_urls.add(candidate.root_url)

    return deduped
