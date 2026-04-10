from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from packages.connectors.domain_discovery import (
    build_candidate_sources,
    infer_vendor_name,
    normalize_domain,
    slugify_name,
)
from packages.contracts.vendor import (
    DiscoveredSourceResponse,
    VendorResolveRequest,
    VendorResolveResponse,
)
from packages.core.models import CrawlJob, Product, Source, Vendor


class VendorResolutionService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def resolve(self, request: VendorResolveRequest) -> VendorResolveResponse:
        domain = normalize_domain(request.input.value)
        canonical_name = infer_vendor_name(domain)
        vendor = self._get_or_create_vendor(domain=domain, canonical_name=canonical_name)
        product = self._get_or_create_primary_product(vendor=vendor)

        sources = self._get_or_create_sources(
            vendor=vendor,
            product=product,
            should_discover=request.options.discover_sources,
        )
        job_ids = self._create_crawl_jobs(
            vendor=vendor,
            product=product,
            sources=sources,
            should_seed=request.options.seed_crawl,
        )

        self.db.commit()

        return VendorResolveResponse(
            vendor_id=str(vendor.vendor_id),
            primary_product_id=str(product.product_id),
            canonical_name=vendor.canonical_name,
            primary_domain=vendor.primary_domain or domain,
            match_confidence=1.0,
            discovered_sources=[
                DiscoveredSourceResponse(
                    source_id=str(source.source_id),
                    source_type=source.source_type,
                    source_family=source.source_family,
                    root_url=source.root_url,
                    connector_type=source.connector_type,
                )
                for source in sources
            ],
            seeded_job_ids=job_ids,
        )

    def _get_or_create_vendor(self, domain: str, canonical_name: str) -> Vendor:
        vendor = self.db.execute(
            select(Vendor).where(Vendor.primary_domain == domain)
        ).scalar_one_or_none()

        if vendor is not None:
            return vendor

        vendor = Vendor(
            canonical_name=canonical_name,
            canonical_slug=slugify_name(canonical_name),
            primary_domain=domain,
            summary_short=f"{canonical_name} vendor profile created from domain resolution.",
            status="active",
        )
        self.db.add(vendor)
        self.db.flush()
        return vendor

    def _get_or_create_primary_product(self, vendor: Vendor) -> Product:
        product = self.db.execute(
            select(Product).where(
                Product.vendor_id == vendor.vendor_id,
                Product.product_type == "core_platform",
            )
        ).scalar_one_or_none()

        if product is not None:
            return product

        product = Product(
            vendor_id=vendor.vendor_id,
            canonical_name=vendor.canonical_name,
            canonical_slug=vendor.canonical_slug,
            product_type="core_platform",
            summary_short=f"Primary product placeholder for {vendor.canonical_name}.",
            status="active",
        )
        self.db.add(product)
        self.db.flush()
        return product

    def _get_or_create_sources(
        self,
        vendor: Vendor,
        product: Product,
        should_discover: bool,
    ) -> list[Source]:
        if not should_discover:
            return list(
                self.db.execute(
                    select(Source).where(Source.vendor_id == vendor.vendor_id).order_by(Source.root_url.asc())
                ).scalars()
            )

        discovered_sources: list[Source] = []
        for candidate in build_candidate_sources(vendor.primary_domain or ""):
            source = self.db.execute(
                select(Source).where(
                    Source.vendor_id == vendor.vendor_id,
                    Source.root_url == candidate.root_url,
                )
            ).scalar_one_or_none()

            if source is None:
                source = Source(
                    vendor_id=vendor.vendor_id,
                    product_id=product.product_id,
                    source_family=candidate.source_family,
                    source_type=candidate.source_type,
                    root_url=candidate.root_url,
                    connector_type=candidate.connector_type,
                    is_active=True,
                    source_metadata=candidate.metadata,
                )
                self.db.add(source)
                self.db.flush()

            discovered_sources.append(source)

        return discovered_sources

    def _create_crawl_jobs(
        self,
        vendor: Vendor,
        product: Product,
        sources: list[Source],
        should_seed: bool,
    ) -> list[str]:
        if not should_seed:
            return []

        job_ids: list[str] = []
        for source in sources:
            existing_job = self.db.execute(
                select(CrawlJob).where(
                    CrawlJob.source_id == source.source_id,
                    CrawlJob.job_type == "fetch_source",
                    CrawlJob.status.in_(["queued", "leased"]),
                )
            ).scalar_one_or_none()
            if existing_job is not None:
                continue

            worker_queue = "browser_fetch" if source.connector_type == "browser" else "api_fetch"
            job = CrawlJob(
                vendor_id=vendor.vendor_id,
                product_id=product.product_id,
                source_id=source.source_id,
                job_type="fetch_source",
                worker_queue=worker_queue,
                status="queued",
                priority=80,
                payload={
                    "vendor_id": str(vendor.vendor_id),
                    "product_id": str(product.product_id),
                    "source_id": str(source.source_id),
                    "root_url": source.root_url,
                    "source_type": source.source_type,
                },
            )
            self.db.add(job)
            self.db.flush()
            job_ids.append(str(job.crawl_job_id))

        return job_ids
