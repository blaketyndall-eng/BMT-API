# Database Setup Runbook

## Local startup

Start the local stack:

```bash
docker compose up -d db
```

Apply the migration:

```bash
python scripts/db_upgrade.py
```

Start the API and worker:

```bash
docker compose up api worker
```

## Verify the API

Healthcheck:

```bash
curl http://localhost:8000/healthz
```

Vendor resolve:

```bash
curl -X POST http://localhost:8000/v1/vendors/resolve \
  -H "Content-Type: application/json" \
  -d '{
    "input": {"type": "domain", "value": "acme.com"},
    "options": {"discover_sources": true, "seed_crawl": true}
  }'
```

## Expected outcome

The resolve endpoint should:
- create or reuse a vendor record
- create or reuse a primary product
- discover likely public source surfaces
- queue crawl jobs for those sources

## Current scope

This is the foundation only.
The worker does not yet lease and execute crawl jobs.
The immediate next implementation step is real job leasing plus the first browser fetch worker.
