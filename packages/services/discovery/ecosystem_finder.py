from __future__ import annotations

from packages.contracts.discovery import DiscoveredSourceCandidate


class EcosystemFinderService:
    def find(self, vendor_domain: str) -> list[DiscoveredSourceCandidate]:
        base = vendor_domain.removeprefix("https://").removeprefix("http://").strip("/")
        vendor_slug = base.split(".")[0]
        return [
            self._candidate(f"https://github.com/{vendor_slug}", "repo", "official_repo_org", "ecosystem_commercial", "green", "api", False, "repo_api", ["repo_metadata_parser"], 0.84, "Likely public source-control organization if it exists."),
            self._candidate(f"https://pypi.org/project/{vendor_slug}", "package_registry", "package_registry", "developer_shipped_truth", "green", "api", True, "registry_api", ["package_registry_parser"], 0.86, "Potential Python package namespace if vendor ships SDKs or CLI tools."),
            self._candidate(f"https://www.npmjs.com/package/{vendor_slug}", "package_registry", "package_registry", "developer_shipped_truth", "green", "api", True, "registry_api", ["package_registry_parser"], 0.86, "Potential npm package namespace if vendor ships JS tooling or SDKs."),
            self._candidate(f"https://www.g2.com/products/{vendor_slug}/reviews", "marketplace", "marketplace_listing", "ecosystem_commercial", "amber", "browser", False, "browser_fetch", ["html_claim_extractor"], 0.68, "Commercial marketplace signal; use with lower confidence and stronger provenance handling."),
        ]

    def _candidate(self, root_url: str, source_family: str, source_type: str, source_group: str, policy_zone: str, connector_type: str, machine_readable: bool, crawler_mode: str, parser_chain: list[str], weight: float, notes: str) -> DiscoveredSourceCandidate:
        return DiscoveredSourceCandidate(
            root_url=root_url,
            source_family=source_family,
            source_type=source_type,
            source_group=source_group,
            policy_zone=policy_zone,
            connector_type=connector_type,
            machine_readable=machine_readable,
            crawler_mode=crawler_mode,
            parser_chain=parser_chain,
            base_confidence_weight=weight,
            provenance_required=True,
            terms_review_required=policy_zone == "amber",
            notes=notes,
        )
