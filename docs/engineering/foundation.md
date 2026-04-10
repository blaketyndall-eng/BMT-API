# Engineering Foundation

## Product stance

BMT-API is an evidence-backed vendor understanding system.

The system should answer:
- what a vendor does
- which capabilities are supported
- who the product is for
- how teams use it
- what it integrates with
- what changed recently
- why the system believes those things

## Core storage model

Store:
1. raw source artifacts
2. evidence
3. claims

Avoid storing only summary blobs.

## First persistent objects

- vendors
- products
- sources
- pages
- crawl_jobs
- crawl_runs
- evidence
- claims
- claim_support

## First endpoints

- `POST /v1/vendors/resolve`
- `POST /v1/crawl/jobs`
- `GET /v1/products/{product_id}/capabilities`
- `GET /v1/products/{product_id}/evidence`

## First sprint objective

Prove the claim graph on a small set of vendors before optimizing for scale.

## Immediate next implementation steps

1. Add Alembic migration support
2. Add SQLAlchemy models for vendors/products/sources/pages
3. Add crawl job leasing with Postgres
4. Add a docs/changelog page classifier
5. Add the first capability evidence extractor
6. Add typed contracts for vendor resolve and capabilities endpoints
