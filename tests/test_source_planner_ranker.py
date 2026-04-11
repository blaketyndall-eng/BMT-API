from packages.contracts.agents import SourceProposal
from packages.services.source_planner_ranker import ProposalHistory, SourcePlannerRanker


def _proposal(url: str, source_type: str, confidence: float) -> SourceProposal:
    return SourceProposal(
        root_url=url,
        source_type=source_type,
        reason="Base reason.",
        target_gap_codes=["missing_docs_surface"],
        confidence=confidence,
    )


def test_rank_prefers_promoted_history_over_rejected_history() -> None:
    ranker = SourcePlannerRanker()
    promoted = _proposal("https://docs.example.com", "docs_subdomain", 0.82)
    rejected = _proposal("https://example.com/docs", "docs_path", 0.84)

    ranked = ranker.rank(
        [rejected, promoted],
        {
            promoted.root_url: ProposalHistory(promoted_count=2, rejected_count=0),
            rejected.root_url: ProposalHistory(promoted_count=0, rejected_count=2),
        },
    )

    assert ranked[0].root_url == promoted.root_url
    assert "previously promoted" in ranked[0].reason.lower()
    assert "previously rejected" in ranked[1].reason.lower()


def test_rank_uses_source_type_prior_when_no_history_exists() -> None:
    ranker = SourcePlannerRanker()
    pricing = _proposal("https://example.com/pricing", "pricing", 0.7)
    homepage = _proposal("https://example.com", "homepage", 0.7)

    ranked = ranker.rank([homepage, pricing], {})

    assert ranked[0].root_url == pricing.root_url
    assert ranked[0].confidence >= ranked[1].confidence


def test_rank_penalizes_existing_coverage_and_failed_crawls() -> None:
    ranker = SourcePlannerRanker()
    cleaner = _proposal("https://docs.example.com", "docs_subdomain", 0.82)
    penalized = _proposal("https://developers.example.com", "developers_subdomain", 0.82)

    ranked = ranker.rank(
        [penalized, cleaner],
        {
            cleaner.root_url: ProposalHistory(promoted_count=1, same_type_existing_count=0, recent_failed_crawls=0),
            penalized.root_url: ProposalHistory(promoted_count=1, same_type_existing_count=3, recent_failed_crawls=2),
        },
    )

    assert ranked[0].root_url == cleaner.root_url
    assert "existing coverage" in ranked[1].reason.lower()
    assert "crawl attempts failed" in ranked[1].reason.lower()
