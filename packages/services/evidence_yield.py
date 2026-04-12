from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from packages.core.models import Evidence, Page


class EvidenceYieldService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def compute(self, source_id: str | uuid.UUID) -> float:
        source_uuid = uuid.UUID(str(source_id))
        evidence_count = int(
            self.db.execute(
                select(func.count(Evidence.evidence_id)).where(Evidence.source_id == source_uuid)
            ).scalar_one()
            or 0
        )
        if evidence_count == 0:
            return 0.0

        avg_confidence = float(
            self.db.execute(
                select(func.avg(Evidence.confidence)).where(Evidence.source_id == source_uuid)
            ).scalar_one()
            or 0.0
        )
        unique_pages = int(
            self.db.execute(
                select(func.count(func.distinct(Evidence.page_id))).where(Evidence.source_id == source_uuid)
            ).scalar_one()
            or 0
        )
        docs_pages = int(
            self.db.execute(
                select(func.count(Page.page_id))
                .where(Page.source_id == source_uuid)
                .where(Page.page_type.in_(["docs", "api_reference", "pricing", "changelog"]))
            ).scalar_one()
            or 0
        )

        count_score = min(evidence_count / 12.0, 1.0)
        page_score = min(unique_pages / 4.0, 1.0)
        docs_score = min(docs_pages / 3.0, 1.0)
        score = (count_score * 0.35) + (avg_confidence * 0.4) + (page_score * 0.15) + (docs_score * 0.1)
        return round(min(score, 1.0), 3)
