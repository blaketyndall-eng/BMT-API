from packages.extraction.claim_normalizer import normalize_claim


def test_normalize_claim_maps_alias_to_canonical_taxonomy_entry() -> None:
    result = normalize_claim(claim_type="capability", label="sso")

    assert result.claim_type == "capability"
    assert result.normalized_key == "single_sign_on"
    assert result.display_label == "Single Sign-On"


def test_normalize_claim_falls_back_to_titleized_display_label() -> None:
    result = normalize_claim(claim_type="change_event", label="custom_release_theme")

    assert result.claim_type == "change_event"
    assert result.normalized_key == "custom_release_theme"
    assert result.display_label == "Custom Release Theme"
