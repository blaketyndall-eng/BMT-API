# Hosted Deployment Setup

## Recommended topology

Create one Railway project with three services:

1. `postgres`
2. `api`
3. `worker`

Use the same GitHub repo for both `api` and `worker`.

## Railway service settings

### API service

- Source: this repo
- Branch: `main`
- Healthcheck path: `/healthz`
- Pre-deploy command: `python scripts/db_upgrade.py`
- Start command: `bash -lc "uvicorn apps.api.main:app --host 0.0.0.0 --port ${PORT:-8000}"`

### Worker service

- Source: this repo
- Branch: `main`
- Start command: `bash -lc "python -m apps.worker.main"`

### Shared variables on API and worker

- `BMT_API_ENV=production`
- `BMT_API_DATABASE_URL=${{Postgres.DATABASE_URL}}`

## GitHub repository secrets and variables

### Secret

- `RAILWAY_TOKEN`

### Variables

- `RAILWAY_PROJECT_ID`
- `RAILWAY_ENVIRONMENT_NAME`
- `RAILWAY_API_SERVICE`
- `RAILWAY_WORKER_SERVICE`
- `BMT_API_BASE_URL`

## Workflows in this repo

### CI

Runs tests on pushes and pull requests.

### Deploy to Railway

Deploys the current repo to the configured Railway API and worker services when secrets and variables are present.

### Seed Vendor

Manual workflow that calls the deployed API and resolves a vendor domain to seed sources and crawl jobs.

## First hosted workflow

1. Create the Railway project and Postgres service.
2. Create the API and worker services from this repo.
3. Add the start commands and pre-deploy command above.
4. Add the repository secret and variables.
5. Run the `Deploy to Railway` workflow or push to `main`.
6. Run the `Seed Vendor` workflow with a domain like `acme.com`.
