# Database Setup Runbook

## Local startup

Start the local stack:

```bash
docker compose up -d db
```

Apply the migrations:

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

## Verify the worker path

After resolving a vendor, the worker should lease a queued `browser_fetch` job and persist a `pages` record for the fetched URL.

## Current scope

This is the first execution path only.
The worker leases and executes `browser_fetch` jobs, but deeper parsing and evidence extraction still need to be added.
