FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000

WORKDIR /app

COPY pyproject.toml README.md ./
COPY alembic.ini ./
COPY apps ./apps
COPY packages ./packages
COPY migrations ./migrations
COPY scripts ./scripts

RUN pip install --upgrade pip && pip install .

CMD ["bash", "-lc", "uvicorn apps.api.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
