from __future__ import annotations

import uuid
from collections import OrderedDict

from sqlalchemy import select
from sqlalchemy.orm import Session

from packages.contracts.agents import AgentRunSummary, SourcePlannerRequest, SourcePlannerResponse, SourceProposal
from packages.core.models import Product, Source, Vendor
from packages.observability.tracing import log_event, traced_span
from packages.services.gap_detector import detect_product_gaps
from packages.services.product_intelligence import ProductIntelligenceService, build_normalized_claims

STRATEGY_VERSION = "source_planner_v1"


class SourcePlannerAgentService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.product_intelligence = ProductIntelligenceService(db)

    def plan(self, request: SourcePlannerRequest) -> SourcePlannerResponse:
        product_id = uuid.UUID(request.product_id)
        with traced_span("agent.source_planner.plan", product_id=request.product_id):
            context = self._get_product_vendor_context(product_id)
            claim_rows = self.product_intelligence._get_claim_rows(product_id)
            claims = build_normalized_claims(rows=claim_rows, include_stale=True, include_evidence=False)
            page_types = self.product_intelligence._get_page_types(product_id)
            gaps = detect_product_gaps(page_types=page_types, claims=claims)
            existing_sources = self._get_existing_sources(product_id)
            proposals = self._build_proposals(
                primary_domain=context["primary_domain"],
                gaps=gaps,
                existing_sources=existing_sources,
                include_existing_sources=request.include_existing_sources,
                max_candidates=request.max_candidates,
            )
            log_event(
                "agent.source_planner.completed",
                product_id=request.product_id,
                gap_count=len(gaps),
                proposal_count=len(proposals),
            )
            return SourcePlannerResponse(
                product_id=request.product_id,
                agent=AgentRunSummary(
                    agent_name="source_planner_agent",
                    strategy_version=STRATEGY_VERSION,
                    mode="heuristic_scaffold",
                ),
                considered_gap_codes=[gap.gap_code for gap in gaps],
                proposals=proposals,
            )

    def _get_product_vendor_context(self, product_id: uuid.UUID) -> dict[str, str | None]:
        row = self.db.execute(
            select(Product, Vendor)
            .join(Vendor, Product.vendor_id == Vendor.vendor_id)
            .where(Product.product_id == product_id)
        ).one_or_none()
        if row is None:
            raise ValueError(f"Product not found: {product_id}")
        product, vendor = row
        return {
            "product_name": product.canonical_name,
            "primary_domain": vendor.primary_domain,
        }

    def _get_existing_sources(self, product_id: uuid.UUID) -> set[str]:
        rows = self.db.execute(select(Source.root_url).where(Source.product_id == product_id)).scalars()
        return set(rows)

    def _build_proposals(
        self,
        *,
        primary_domain: str | None,
        gaps,
        existing_sources: set[str],
        include_existing_sources: bool,
        max_candidates: int,
    ) -> list[SourceProposal]:
        if not primary_domain:
            return []

        candidates: OrderedDict[str, SourceProposal] = OrderedDict()

        def add(url: str, source_type: str, reason: str, gap_code: str, confidence: float) -> None:
            if not include_existing_sources and url in existing_sources:
                return
            if url in candidates:
                proposal = candidates[url]
                if gap_code not in proposal.target_gap_codes:
                    proposal.target_gap_codes.append(gap_code)
                return
            candidates[url] = SourceProposal(
                root_url=url,
                source_type=source_type,
                reason=reason,
                target_gap_codes=[gap_code],
                confidence=confidence,
            )

        for gap in gaps:
            if gap.gap_code == "missing_pricing_page":
                add(
                    f"https://{primary_domain}/pricing",
                    "pricing",
                    "Pricing coverage is missing, so the canonical pricing page is the highest-leverage next source.",
                    gap.gap_code,
                    0.93,
                )
            elif gap.gap_code == "missing_docs_surface":
                add(
                    f"https://docs.{primary_domain}",
                    "docs_subdomain",
                    "Docs coverage is missing, so the docs subdomain is the most likely source of durable feature evidence.",
                    gap.gap_code,
                    0.9,
                )
                add(
                    f"https://{primary_domain}/docs",
                    "docs_path",
                    "The docs path often exposes product capabilities and integration proof when docs live on the main domain.",
                    gap.gap_code,
                    0.84,
                )
                add(
                    f"https://developers.{primary_domain}",
                    "developers_subdomain",
                    "A developers subdomain often contains API and integration evidence when user docs are sparse.",
                    gap.gap_code,
                    0.82,
                )
            elif gap.gap_code == "missing_change_surface":
                add(
                    f"https://{primary_domain}/changelog",
                    "changelog",
                    "Change coverage is missing, so a changelog is the highest-signal source for freshness and release evidence.",
                    gap.gap_code,
                    0.88,
                )
                add(
                    f"https://{primary_domain}/release-notes",
                    "release_notes",
                    "Release notes are a common alternative when no changelog surface is present.",
                    gap.gap_code,
                    0.84,
                )
            elif gap.gap_code == "integrations_thin_support":
                add(
                    f"https://{primary_domain}/integrations",
                    "integrations_directory",
                    "Integration claims are thinly supported, so the integrations directory is the best next source to deepen proof.",
                    gap.gap_code,
                    0.86,
                )
            elif gap.gap_code == "claims_stale":
                add(
                    f"https://{primary_domain}",
                    "homepage",
                    "Claims are stale, so the homepage is a good refresh point before recrawling deeper sources.",
                    gap.gap_code,
                    0.62,
                )

        return list(candidates.values())[:max_candidates]
