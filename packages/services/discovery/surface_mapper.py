from __future__ import annotations

from packages.contracts.discovery import DiscoveredSourceCandidate


class SurfaceMapperService:
    def map_vendor_surfaces(self, vendor_domain: str) -> list[DiscoveredSourceCandidate]:
        base = vendor_domain.removeprefix("https://").removeprefix("http://").strip("/")
        candidates = [
            self._candidate(f"https://{base}", "vendor_owned", "homepage", "canonical_vendor_truth", machine_readable=False, crawler_mode="html_fetch", parser_chain=["html_claim_extractor"], weight=0.9, notes="Primary vendor homepage."),
            self._candidate(f"https://{base}/pricing", "vendor_owned", "pricing", "canonical_vendor_truth", machine_readable=False, crawler_mode="html_fetch", parser_chain=["html_claim_extractor"], weight=0.9, notes="Canonical pricing surface."),
            self._candidate(f"https://docs.{base}", "vendor_owned", "docs_subdomain", "developer_shipped_truth", machine_readable=False, crawler_mode="browser_fetch", parser_chain=["docs_nav_parser", "html_claim_extractor"], weight=0.92, notes="Docs subdomain if present."),
            self._candidate(f"https://{base}/docs", "vendor_owned", "docs_path", "developer_shipped_truth", machine_readable=False, crawler_mode="browser_fetch", parser_chain=["docs_nav_parser", "html_claim_extractor"], weight=0.9, notes="Docs path if docs live on main domain."),
            self._candidate(f"https://developers.{base}", "vendor_owned", "developers_subdomain", "developer_shipped_truth", machine_readable=False, crawler_mode="browser_fetch", parser_chain=["docs_nav_parser", "html_claim_extractor"], weight=0.9, notes="Developer portal or API hub."),
            self._candidate(f"https://{base}/integrations", "vendor_owned", "integrations_directory", "canonical_vendor_truth", machine_readable=False, crawler_mode="html_fetch", parser_chain=["html_claim_extractor"], weight=0.88, notes="Integrations directory if present."),
            self._candidate(f"https://{base}/changelog", "vendor_owned", "changelog", "canonical_vendor_truth", machine_readable=False, crawler_mode="html_fetch", parser_chain=["html_claim_extractor"], weight=0.88, notes="Changelog or product updates surface."),
            self._candidate(f"https://{base}/release-notes", "vendor_owned", "release_notes", "canonical_vendor_truth", machine_readable=False, crawler_mode="html_fetch", parser_chain=["html_claim_extractor"], weight=0.84, notes="Release notes surface if present."),
            self._candidate(f"https://status.{base}", "vendor_owned", "status_page", "operational_trust", machine_readable=False, crawler_mode="html_fetch", parser_chain=["statuspage_parser", "html_claim_extractor"], weight=0.87, notes="Status page if vendor hosts one on subdomain."),
            self._candidate(f"https://{base}/security", "vendor_owned", "trust_center", "operational_trust", machine_readable=False, crawler_mode="html_fetch", parser_chain=["html_claim_extractor"], weight=0.88, notes="Trust or security landing page."),
        ]
        return candidates

    def _candidate(self, root_url: str, source_family: str, source_type: str, source_group: str, *, machine_readable: bool, crawler_mode: str, parser_chain: list[str], weight: float, notes: str | None) -> DiscoveredSourceCandidate:
        return DiscoveredSourceCandidate(
            root_url=root_url,
            source_family=source_family,
            source_type=source_type,
            source_group=source_group,
            policy_zone="green",
            connector_type="browser",
            machine_readable=machine_readable,
            crawler_mode=crawler_mode,
            parser_chain=parser_chain,
            base_confidence_weight=weight,
            provenance_required=True,
            terms_review_required=False,
            notes=notes,
        )
