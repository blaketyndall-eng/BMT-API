from packages.extraction.evidence_extractors import extract_page_evidence


def test_extract_capability_and_integration_evidence_from_docs_page() -> None:
    text = (
        "Our platform supports single sign-on and audit logs. "
        "It also integrates with Salesforce and Slack for workflow automation."
    )

    items = extract_page_evidence(page_type="docs", title="Docs", page_text=text)
    labels = {(item.evidence_type, item.label) for item in items}

    assert ("capability", "single_sign_on") in labels
    assert ("capability", "audit_logs") in labels
    assert ("integration", "salesforce") in labels
    assert ("integration", "slack") in labels


def test_extract_change_event_evidence_from_changelog_page() -> None:
    text = (
        "We added webhook support for downstream automation. "
        "We improved dashboard performance across large workspaces."
    )

    items = extract_page_evidence(page_type="changelog", title="Release Notes", page_text=text)

    assert any(item.evidence_type == "change_event" for item in items)
    assert any("added webhook support" in item.snippet.lower() for item in items)
