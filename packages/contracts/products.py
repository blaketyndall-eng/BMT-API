from datetime import datetime

from pydantic import BaseModel


class ClaimEvidenceRef(BaseModel):
    evidence_id: str
    page_id: str | None
    canonical_url: str | None
    snippet: str
    confidence: float
    created_at: datetime


class CapabilityClaim(BaseModel):
    claim_type: str
    label: str
    confidence: float
    support_count: int
    latest_evidence_at: datetime | None
    evidence: list[ClaimEvidenceRef]


class ProductCapabilitiesResponse(BaseModel):
    product_id: str
    items: list[CapabilityClaim]


class ProductEvidenceItem(BaseModel):
    evidence_id: str
    evidence_type: str
    label: str
    snippet: str
    confidence: float
    canonical_url: str | None
    page_id: str | None
    created_at: datetime
    updated_at: datetime


class ProductEvidenceResponse(BaseModel):
    product_id: str
    items: list[ProductEvidenceItem]
