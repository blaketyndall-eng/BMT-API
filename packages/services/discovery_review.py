from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from packages.contracts.discovery_review import (
    DiscoveryCandidateReviewItem,
    DiscoveryCandidateReviewListResponse,
)
from packages.core.models import AgentRun
from packages.services.registry_manager import DISCOVERY_AGENT_NAME


class DiscoveryReviewService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_candidates(
        self,
        *,
        vendor_domain: str | None,
        source_group: str | None,
        policy_zone: str | None,
        limit: int,
    ) -> DiscoveryCandidateReviewListResponse:
        stmt = (
            select(AgentRun)
            .where(AgentRun.agent_name == DISCOVERY_AGENT_NAME)
            .order_by(AgentRun.created_at.desc())
            .limit(limit)
        )
        runs = self.db.execute(stmt).scalars()

        items: list[DiscoveryCandidateReviewItem] = []
        seen: set[tuple[str, str]] = set()
        for run in runs:
            response_payload = run.response_payload or {}
            run_vendor_domain = response_payload.get("vendor_domain")
            if vendor_domain and run_vendor_domain != vendor_domain:
                continue
            for candidate in response_payload.get("candidates", []):
                if source_group and candidate.get("source_group") != source_group:
                    continue
                if policy_zone and candidate.get("policy_zone") != policy_zone:
                    continue
                dedupe_key = (run_vendor_domain or "", candidate.get("root_url") or "")
                if dedupe_key in seen:
                    continue
                seen.add(dedupe_key)
                items.append(
                    DiscoveryCandidateReviewItem(
                        discovery_run_id=str(run.agent_run_id),
                        vendor_domain=run_vendor_domain or "",
                        root_url=candidate.get("root_url", ""),
                        source_family=candidate.get("source_family", ""),
                        source_type=candidate.get("source_type", ""),
                        source_group=candidate.get("source_group", ""),
                        policy_zone=candidate.get("policy_zone", ""),
                        connector_type=candidate.get("connector_type", ""),
                        machine_readable=bool(candidate.get("machine_readable", False)),
                        crawler_mode=candidate.get("crawler_mode", ""),
                        parser_chain=list(candidate.get("parser_chain", [])),
                        base_confidence_weight=float(candidate.get("base_confidence_weight", 0.0)),
                        provenance_required=bool(candidate.get("provenance_required", True)),
                        terms_review_required=bool(candidate.get("terms_review_required", False)),
                        notes=candidate.get("notes"),
                        trace_id=run.trace_id,
                        created_at=run.created_at,
                    )
                )
        return DiscoveryCandidateReviewListResponse(items=items)
