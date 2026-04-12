from __future__ import annotations

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from packages.contracts.entity_resolution import (
    EntityResolutionRequest,
    EntityResolutionResponse,
    ProductResolutionMatch,
    VendorResolutionMatch,
)
from packages.core.models import Product, Vendor


class EntityResolutionService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def resolve(self, request: EntityResolutionRequest) -> EntityResolutionResponse:
        vendor_matches = self._resolve_vendors(request)
        product_matches = self._resolve_products(request, vendor_matches)
        return EntityResolutionResponse(
            vendor_domain=request.vendor_domain,
            root_url=request.root_url,
            artifact_slug=request.artifact_slug,
            vendor_matches=vendor_matches,
            product_matches=product_matches,
        )

    def _resolve_vendors(self, request: EntityResolutionRequest) -> list[VendorResolutionMatch]:
        domain = self._normalize_domain(request.vendor_domain or request.root_url)
        slug = self._normalize_slug(request.artifact_slug or domain)
        if not domain and not slug:
            return []

        clauses = []
        if domain:
            clauses.append(Vendor.primary_domain == domain)
        if slug:
            clauses.append(Vendor.canonical_slug == slug)
        rows = self.db.execute(select(Vendor).where(or_(*clauses))).scalars() if clauses else []

        matches: list[VendorResolutionMatch] = []
        for vendor in rows:
            reason, confidence = self._vendor_reason_and_confidence(vendor, domain, slug)
            matches.append(
                VendorResolutionMatch(
                    vendor_id=str(vendor.vendor_id),
                    canonical_name=vendor.canonical_name,
                    canonical_slug=vendor.canonical_slug,
                    primary_domain=vendor.primary_domain,
                    match_reason=reason,
                    confidence=confidence,
                )
            )
        return sorted(matches, key=lambda item: item.confidence, reverse=True)

    def _resolve_products(
        self,
        request: EntityResolutionRequest,
        vendor_matches: list[VendorResolutionMatch],
    ) -> list[ProductResolutionMatch]:
        slug = self._normalize_slug(request.artifact_slug or request.root_url or request.vendor_domain)
        if not slug:
            return []

        vendor_ids = [match.vendor_id for match in vendor_matches]
        stmt = select(Product)
        if vendor_ids:
            from uuid import UUID
            stmt = stmt.where(Product.vendor_id.in_([UUID(vendor_id) for vendor_id in vendor_ids]))
        stmt = stmt.where(Product.canonical_slug == slug)
        rows = self.db.execute(stmt).scalars()

        matches: list[ProductResolutionMatch] = []
        for product in rows:
            matches.append(
                ProductResolutionMatch(
                    product_id=str(product.product_id),
                    canonical_name=product.canonical_name,
                    canonical_slug=product.canonical_slug,
                    vendor_id=str(product.vendor_id),
                    match_reason="Product slug matched artifact slug within resolved vendor scope.",
                    confidence=0.88 if vendor_ids else 0.74,
                )
            )
        return matches

    def _vendor_reason_and_confidence(self, vendor: Vendor, domain: str | None, slug: str | None) -> tuple[str, float]:
        domain_match = bool(domain and vendor.primary_domain == domain)
        slug_match = bool(slug and vendor.canonical_slug == slug)
        if domain_match and slug_match:
            return "Primary domain and canonical slug both matched.", 0.96
        if domain_match:
            return "Primary domain matched vendor domain.", 0.91
        if slug_match:
            return "Canonical slug matched artifact slug.", 0.78
        return "Weak deterministic match.", 0.55

    def _normalize_domain(self, value: str | None) -> str | None:
        if not value:
            return None
        cleaned = value.removeprefix("https://").removeprefix("http://").split("/")[0].strip().lower()
        if cleaned.startswith("www."):
            cleaned = cleaned[4:]
        return cleaned or None

    def _normalize_slug(self, value: str | None) -> str | None:
        if not value:
            return None
        cleaned = value.removeprefix("https://").removeprefix("http://").split("/")[0].strip().lower()
        if cleaned.startswith("www."):
            cleaned = cleaned[4:]
        slug = cleaned.split(".")[0]
        slug = slug.replace("_", "-")
        return slug or None
