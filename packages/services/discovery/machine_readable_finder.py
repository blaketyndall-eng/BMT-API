from __future__ import annotations

from packages.contracts.discovery import DiscoveredSourceCandidate


class MachineReadableFinderService:
    def find(self, vendor_domain: str) -> list[DiscoveredSourceCandidate]:
        base = vendor_domain.removeprefix("https://").removeprefix("http://").strip("/")
        return [
            self._candidate(f"https://{base}/robots.txt", "vendor_owned", "robots_txt", "canonical_vendor_truth", ["robots_parser"], 0.78, "Robots coordination surface."),
            self._candidate(f"https://{base}/sitemap.xml", "vendor_owned", "sitemap", "canonical_vendor_truth", ["sitemap_parser"], 0.84, "Primary sitemap discovery surface."),
            self._candidate(f"https://{base}/.well-known/security.txt", "vendor_owned", "security_txt", "operational_trust", ["security_txt_parser"], 0.88, "Machine-readable security disclosure surface."),
            self._candidate(f"https://{base}/openapi.json", "vendor_owned", "openapi", "developer_shipped_truth", ["openapi_parser"], 0.92, "OpenAPI spec if exposed on main domain."),
            self._candidate(f"https://docs.{base}/openapi.json", "vendor_owned", "openapi", "developer_shipped_truth", ["openapi_parser"], 0.92, "OpenAPI spec if exposed on docs domain."),
            self._candidate(f"https://{base}/llms.txt", "machine_readable_public", "llms_txt", "hidden_public_machine_readable", ["llms_txt_parser"], 0.7, "AI-oriented site summary if present."),
            self._candidate(f"https://{base}/manifest.json", "machine_readable_public", "docs_nav_json", "hidden_public_machine_readable", ["docs_nav_parser"], 0.72, "Common public manifest/bootstrap entrypoint."),
        ]

    def _candidate(self, root_url: str, source_family: str, source_type: str, source_group: str, parser_chain: list[str], weight: float, notes: str) -> DiscoveredSourceCandidate:
        return DiscoveredSourceCandidate(
            root_url=root_url,
            source_family=source_family,
            source_type=source_type,
            source_group=source_group,
            policy_zone="amber" if source_group == "hidden_public_machine_readable" else "green",
            connector_type="api" if source_type in {"openapi", "docs_nav_json"} else "browser",
            machine_readable=True,
            crawler_mode="machine_readable_fetch",
            parser_chain=parser_chain,
            base_confidence_weight=weight,
            provenance_required=True,
            terms_review_required=source_group == "hidden_public_machine_readable",
            notes=notes,
        )
