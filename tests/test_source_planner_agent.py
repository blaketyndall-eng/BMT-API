from packages.contracts.product_intelligence import GapItem
from packages.services.source_planner_agent import SourcePlannerAgentService


def test_build_proposals_prioritizes_gap_closure_and_dedupes_existing_sources() -> None:
    service = SourcePlannerAgentService(db=None)  # type: ignore[arg-type]
    gaps = [
        GapItem(
            gap_code="missing_pricing_page",
            category="pricing",
            severity="high",
            message="Missing pricing page.",
            evidence_count=0,
            suggested_source_types=["pricing"],
        ),
        GapItem(
            gap_code="missing_docs_surface",
            category="docs",
            severity="high",
            message="Missing docs surface.",
            evidence_count=0,
            suggested_source_types=["docs_subdomain"],
        ),
    ]

    proposals = service._build_proposals(
        primary_domain="example.com",
        gaps=gaps,
        existing_sources={"https://example.com/pricing"},
        include_existing_sources=False,
        max_candidates=5,
    )

    urls = [proposal.root_url for proposal in proposals]
    assert "https://example.com/pricing" not in urls
    assert "https://docs.example.com" in urls
    assert any("missing_docs_surface" in proposal.target_gap_codes for proposal in proposals)
