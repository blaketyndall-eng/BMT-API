from __future__ import annotations


class MachineReadableFinderService:
    def map_machine_readable_surfaces(self, *, domain: str) -> list[dict]:
        root = f"https://{domain}"
        return [
            {"root_url": f"{root}/robots.txt", "source_family": "machine_readable_public", "source_type": "robots_txt", "connector_type": "api"},
            {"root_url": f"{root}/sitemap.xml", "source_family": "machine_readable_public", "source_type": "sitemap", "connector_type": "api"},
            {"root_url": f"{root}/llms.txt", "source_family": "machine_readable_public", "source_type": "llms_txt", "connector_type": "api"},
            {"root_url": f"{root}/.well-known/security.txt", "source_family": "machine_readable_public", "source_type": "security_txt", "connector_type": "api"},
            {"root_url": f"{root}/openapi.json", "source_family": "machine_readable_public", "source_type": "openapi", "connector_type": "api"},
            {"root_url": f"{root}/swagger.json", "source_family": "machine_readable_public", "source_type": "openapi", "connector_type": "api"},
            {"root_url": f"https://docs.{domain}/openapi.json", "source_family": "machine_readable_public", "source_type": "openapi", "connector_type": "api"},
            {"root_url": f"https://docs.{domain}/search-index.json", "source_family": "machine_readable_public", "source_type": "docs_nav_json", "connector_type": "api"},
        ]
