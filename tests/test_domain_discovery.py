from packages.connectors.domain_discovery import (
    build_candidate_sources,
    infer_vendor_name,
    normalize_domain,
)


def test_normalize_domain_strips_scheme_path_and_www() -> None:
    assert normalize_domain("https://www.example.com/docs/start") == "example.com"


def test_infer_vendor_name_from_domain() -> None:
    assert infer_vendor_name("deep-market.io") == "Deep Market"


def test_build_candidate_sources_includes_homepage_docs_and_status() -> None:
    sources = build_candidate_sources("example.com")
    source_types = {source.source_type for source in sources}

    assert "homepage" in source_types
    assert "docs_subdomain" in source_types
    assert "status" in source_types
