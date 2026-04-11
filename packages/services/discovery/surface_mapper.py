from __future__ import annotations


class SurfaceMapperService:
    def map_vendor_surfaces(self, *, domain: str, include_ecosystem: bool = False) -> list[dict]:
        root = f"https://{domain}"
        candidates = [
            {"root_url": root, "source_family": "vendor_owned", "source_type": "homepage", "connector_type": "browser"},
            {"root_url": f"{root}/pricing", "source_family": "vendor_owned", "source_type": "pricing", "connector_type": "browser"},
            {"root_url": f"https://docs.{domain}", "source_family": "vendor_owned", "source_type": "docs_subdomain", "connector_type": "browser"},
            {"root_url": f"{root}/docs", "source_family": "vendor_owned", "source_type": "docs_path", "connector_type": "browser"},
            {"root_url": f"https://developers.{domain}", "source_family": "vendor_owned", "source_type": "developers_subdomain", "connector_type": "browser"},
            {"root_url": f"{root}/integrations", "source_family": "vendor_owned", "source_type": "integrations_directory", "connector_type": "browser"},
            {"root_url": f"{root}/changelog", "source_family": "vendor_owned", "source_type": "changelog", "connector_type": "browser"},
            {"root_url": f"{root}/release-notes", "source_family": "vendor_owned", "source_type": "release_notes", "connector_type": "browser"},
            {"root_url": f"{root}/trust", "source_family": "vendor_owned", "source_type": "trust_center", "connector_type": "browser"},
            {"root_url": f"{root}/security", "source_family": "vendor_owned", "source_type": "security_page", "connector_type": "browser"},
            {"root_url": f"https://status.{domain}", "source_family": "vendor_owned", "source_type": "status_page", "connector_type": "browser"},
        ]
        if include_ecosystem:
            candidates.extend(
                [
                    {"root_url": f"https://github.com/{domain.split('.')[0]}", "source_family": "repo", "source_type": "official_repo_org", "connector_type": "browser"},
                    {"root_url": f"https://www.npmjs.com/search?q={domain.split('.')[0]}", "source_family": "package_registry", "source_type": "package_registry", "connector_type": "browser"},
                ]
            )
        return candidates
