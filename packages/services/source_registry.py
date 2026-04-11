from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from packages.contracts.source_registry import SourceRegistryEntry, SourceRegistryListResponse
from packages.core.models import Source

_MACHINE_READABLE_TYPES = {
    "status_api",
    "openapi",
    "package_registry",
    "docs_nav_json",
    "jsonld_feed",
    "sitemap",
    "security_txt",
}


class SourceRegistryService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_registry_entries(self, *, product_id: str | None = None, source_group: str | None = None, policy_zone: str | None = None, limit: int = 200) -> SourceRegistryListResponse:
        stmt = select(Source).order_by(Source.created_at.desc()).limit(limit)
        if product_id:
            from uuid import UUID
            stmt = stmt.where(Source.product_id == UUID(product_id))

        rows = self.db.execute(stmt).scalars()
        items = [self._to_registry_entry(source) for source in rows]
        if source_group:
            items = [item for item in items if item.source_group == source_group]
        if policy_zone:
            items = [item for item in items if item.policy_zone == policy_zone]
        return SourceRegistryListResponse(items=items)

    def _to_registry_entry(self, source: Source) -> SourceRegistryEntry:
        source_group = self._source_group(source)
        policy_zone = self._policy_zone(source)
        machine_readable = source.source_type in _MACHINE_READABLE_TYPES
        return SourceRegistryEntry(
            source_id=str(source.source_id),
            vendor_id=str(source.vendor_id) if source.vendor_id else None,
            product_id=str(source.product_id) if source.product_id else None,
            root_url=source.root_url,
            source_family=source.source_family,
            source_group=source_group,
            source_type=source.source_type,
            policy_zone=policy_zone,
            connector_type=source.connector_type,
            machine_readable=machine_readable,
            crawler_mode=self._crawler_mode(source, machine_readable),
            parser_chain=self._parser_chain(source),
            base_confidence_weight=self._base_confidence_weight(source_group, source.source_type),
            freshness_profile=self._freshness_profile(source.source_type),
            refresh_cadence=self._refresh_cadence(source.source_type),
            provenance_required=True,
            terms_review_required=policy_zone == "amber",
            notes=self._notes(source),
        )

    def _source_group(self, source: Source) -> str:
        if source.source_family == "vendor_owned":
            if source.source_type in {"docs_subdomain", "docs_path", "developers_subdomain", "openapi"}:
                return "developer_shipped_truth"
            if source.source_type in {"status_page", "status_api", "trust_center", "security_txt"}:
                return "operational_trust"
            return "canonical_vendor_truth"
        if source.source_family in {"package_registry", "repo", "marketplace", "partner_directory"}:
            return "ecosystem_commercial"
        if source.source_family in {"public_json", "machine_readable_public"}:
            return "hidden_public_machine_readable"
        return "ecosystem_commercial"

    def _policy_zone(self, source: Source) -> str:
        if source.source_family in {"public_json", "machine_readable_public"}:
            return "amber"
        return "green"

    def _crawler_mode(self, source: Source, machine_readable: bool) -> str:
        if machine_readable:
            return "machine_readable_fetch"
        if source.connector_type == "browser":
            return "browser_fetch"
        if source.connector_type == "api":
            return "json_endpoint"
        return "html_fetch"

    def _parser_chain(self, source: Source) -> list[str]:
        parser_chain: list[str] = []
        if source.source_type == "sitemap":
            parser_chain.append("sitemap_parser")
        if source.source_type == "security_txt":
            parser_chain.append("security_txt_parser")
        if source.source_type == "openapi":
            parser_chain.append("openapi_parser")
        if source.source_type in {"docs_nav_json", "docs_subdomain", "docs_path", "developers_subdomain"}:
            parser_chain.append("docs_nav_parser")
        if source.source_type == "status_api":
            parser_chain.append("statuspage_parser")
        if source.source_family == "package_registry":
            parser_chain.append("package_registry_parser")
        parser_chain.append("html_claim_extractor")
        return parser_chain

    def _base_confidence_weight(self, source_group: str, source_type: str) -> float:
        if source_group == "developer_shipped_truth":
            return 0.92
        if source_group == "canonical_vendor_truth":
            return 0.9
        if source_group == "operational_trust":
            return 0.88
        if source_type == "package_registry":
            return 0.86
        if source_group == "hidden_public_machine_readable":
            return 0.72
        return 0.68

    def _freshness_profile(self, source_type: str) -> str:
        if source_type in {"status_page", "status_api", "changelog", "release_notes"}:
            return "high_volatility"
        if source_type in {"pricing", "integrations_directory", "docs_subdomain", "docs_path"}:
            return "medium_volatility"
        return "low_volatility"

    def _refresh_cadence(self, source_type: str) -> str:
        if source_type in {"status_page", "status_api"}:
            return "daily"
        if source_type in {"pricing", "changelog", "release_notes", "docs_subdomain", "docs_path", "developers_subdomain", "integrations_directory"}:
            return "weekly"
        return "monthly"

    def _notes(self, source: Source) -> str | None:
        if self._policy_zone(source) == "amber":
            return "Public but higher-scrutiny surface; require provenance logging and tighter rate control."
        if source.source_type == "security_txt":
            return "Use /.well-known/security.txt when available."
        if source.source_type == "sitemap":
            return "Use lastmod as freshness hint, not as sole truth signal."
        return None
