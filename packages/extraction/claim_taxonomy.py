from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ClaimTaxonomyEntry:
    claim_type: str
    normalized_key: str
    display_label: str
    aliases: tuple[str, ...] = ()


_TAXONOMY = (
    ClaimTaxonomyEntry("capability", "single_sign_on", "Single Sign-On", aliases=("sso",)),
    ClaimTaxonomyEntry("capability", "scim_provisioning", "SCIM Provisioning"),
    ClaimTaxonomyEntry("capability", "audit_logs", "Audit Logs"),
    ClaimTaxonomyEntry("capability", "webhooks", "Webhooks"),
    ClaimTaxonomyEntry("capability", "api_access", "API Access"),
    ClaimTaxonomyEntry("capability", "workflow_automation", "Workflow Automation"),
    ClaimTaxonomyEntry("capability", "analytics_reporting", "Analytics & Reporting"),
    ClaimTaxonomyEntry("capability", "dashboards", "Dashboards"),
    ClaimTaxonomyEntry("capability", "search", "Search"),
    ClaimTaxonomyEntry("capability", "templates", "Templates"),
    ClaimTaxonomyEntry("capability", "notifications", "Notifications"),
    ClaimTaxonomyEntry(
        "capability",
        "role_based_access_control",
        "Role-Based Access Control",
        aliases=("rbac",),
    ),
    ClaimTaxonomyEntry("capability", "exports", "Exports"),
    ClaimTaxonomyEntry("integration", "salesforce", "Salesforce"),
    ClaimTaxonomyEntry("integration", "slack", "Slack"),
    ClaimTaxonomyEntry("integration", "jira", "Jira"),
    ClaimTaxonomyEntry("integration", "hubspot", "HubSpot"),
    ClaimTaxonomyEntry("integration", "microsoft_teams", "Microsoft Teams"),
    ClaimTaxonomyEntry("integration", "google_drive", "Google Drive"),
    ClaimTaxonomyEntry("integration", "sharepoint", "SharePoint"),
    ClaimTaxonomyEntry("integration", "box", "Box"),
    ClaimTaxonomyEntry("integration", "okta", "Okta"),
    ClaimTaxonomyEntry("integration", "azure_ad", "Azure AD", aliases=("entra_id",)),
    ClaimTaxonomyEntry("integration", "zapier", "Zapier"),
    ClaimTaxonomyEntry("integration", "github", "GitHub"),
)

_TAXONOMY_INDEX: dict[tuple[str, str], ClaimTaxonomyEntry] = {}
for entry in _TAXONOMY:
    _TAXONOMY_INDEX[(entry.claim_type, entry.normalized_key)] = entry
    for alias in entry.aliases:
        _TAXONOMY_INDEX[(entry.claim_type, alias)] = entry


def _format_display_label(normalized_key: str) -> str:
    return " ".join(token.capitalize() for token in normalized_key.split("_"))


def get_claim_taxonomy_entry(claim_type: str, label: str) -> ClaimTaxonomyEntry:
    normalized_label = label.strip().lower()
    entry = _TAXONOMY_INDEX.get((claim_type, normalized_label))
    if entry is not None:
        return entry

    return ClaimTaxonomyEntry(
        claim_type=claim_type,
        normalized_key=normalized_label,
        display_label=_format_display_label(normalized_label),
    )
