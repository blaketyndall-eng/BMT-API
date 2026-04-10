from packages.extraction.page_classifier import classify_page


def test_classify_docs_page_from_docs_subdomain() -> None:
    result = classify_page(
        requested_url="https://docs.example.com",
        final_url="https://docs.example.com/getting-started",
        title="Getting Started | Example Docs",
        page_text="Documentation and guides for integrating Example.",
        source_type="docs_subdomain",
    )

    assert result.page_type == "docs"
    assert result.confidence >= 0.9


def test_classify_pricing_page_from_url_and_text() -> None:
    result = classify_page(
        requested_url="https://example.com/pricing",
        final_url="https://example.com/pricing",
        title="Pricing | Example",
        page_text="Choose a plan. Contact sales or pay per month.",
        source_type="pricing",
    )

    assert result.page_type == "pricing"
    assert result.confidence >= 0.9


def test_classify_changelog_page_from_release_notes_path() -> None:
    result = classify_page(
        requested_url="https://example.com/release-notes",
        final_url="https://example.com/release-notes",
        title="Release Notes",
        page_text="What\'s new in the product.",
        source_type="release_notes",
    )

    assert result.page_type == "changelog"
    assert result.confidence >= 0.9
