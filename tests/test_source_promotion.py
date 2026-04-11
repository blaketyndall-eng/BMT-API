from uuid import uuid4

from packages.contracts.agents import SourceProposal
from packages.contracts.source_promotion import (
    PromoteSourceProposalRequest,
    RejectSourceProposalRequest,
)
from packages.services.source_promotion import SourcePromotionService


class DummyProduct:
    def __init__(self) -> None:
        self.product_id = uuid4()
        self.vendor_id = uuid4()
        self.canonical_name = "Example Product"


class DummyVendor:
    def __init__(self, vendor_id) -> None:
        self.vendor_id = vendor_id
        self.canonical_name = "Example Vendor"


class DummySource:
    def __init__(self) -> None:
        self.source_id = uuid4()
        self.vendor_id = uuid4()
        self.product_id = uuid4()
        self.connector_type = "browser"
        self.root_url = "https://docs.example.com"
        self.source_type = "docs_subdomain"


class DummyScalarResult:
    def __init__(self, value) -> None:
        self._value = value

    def scalar_one_or_none(self):
        return self._value


class DummyRowResult:
    def __init__(self, value) -> None:
        self._value = value

    def one_or_none(self):
        return self._value


class DummySession:
    def __init__(self, product=None, vendor=None, existing_source=None, existing_job=None) -> None:
        self.product = product
        self.vendor = vendor
        self.existing_source = existing_source
        self.existing_job = existing_job
        self.added = []
        self._execute_count = 0

    def execute(self, stmt):
        self._execute_count += 1
        if self._execute_count == 1:
            return DummyRowResult((self.product, self.vendor))
        if self._execute_count == 2:
            return DummyScalarResult(self.existing_source)
        return DummyScalarResult(self.existing_job)

    def add(self, obj):
        self.added.append(obj)
        if getattr(obj, "source_id", None) is None and hasattr(obj, "root_url"):
            obj.source_id = uuid4()
            obj.vendor_id = self.vendor.vendor_id
            obj.product_id = self.product.product_id
        if getattr(obj, "crawl_job_id", None) is None and hasattr(obj, "job_type"):
            obj.crawl_job_id = uuid4()

    def flush(self):
        return None

    def commit(self):
        return None


def _proposal() -> SourceProposal:
    return SourceProposal(
        root_url="https://docs.example.com",
        source_type="docs_subdomain",
        reason="Docs coverage is missing.",
        target_gap_codes=["missing_docs_surface"],
        confidence=0.9,
    )


def test_promote_creates_source_and_crawl_job_when_missing() -> None:
    product = DummyProduct()
    vendor = DummyVendor(product.vendor_id)
    session = DummySession(product=product, vendor=vendor, existing_source=None, existing_job=None)

    result = SourcePromotionService(session).promote(
        PromoteSourceProposalRequest(
            product_id=str(product.product_id),
            proposal=_proposal(),
            create_crawl_job=True,
            crawl_priority=91,
        )
    )

    assert result.created_source is True
    assert result.created_crawl_job is True
    assert result.deduped_existing_source is False
    assert len(session.added) == 2


def test_reject_returns_structured_response() -> None:
    service = SourcePromotionService(db=None)  # type: ignore[arg-type]

    result = service.reject(
        RejectSourceProposalRequest(
            product_id="00000000-0000-0000-0000-000000000001",
            proposal=_proposal(),
            reason="Low-confidence source guess.",
        )
    )

    assert result.rejected is True
    assert result.reason == "Low-confidence source guess."
    assert result.proposal_root_url == "https://docs.example.com"
