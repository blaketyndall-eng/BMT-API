from __future__ import annotations

import argparse
import json
import os
import sys

import httpx


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed a vendor by calling the deployed BMT API.")
    parser.add_argument("--domain", required=True, help="Vendor domain to resolve and seed")
    parser.add_argument(
        "--base-url",
        default=os.environ.get("BMT_API_BASE_URL", "").strip(),
        help="Base URL for the deployed API. Defaults to BMT_API_BASE_URL.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.base_url:
        print("Missing base URL. Set BMT_API_BASE_URL or pass --base-url.", file=sys.stderr)
        return 1

    base_url = args.base_url.rstrip("/")
    payload = {
        "input": {"type": "domain", "value": args.domain},
        "options": {"discover_sources": True, "seed_crawl": True},
    }

    with httpx.Client(timeout=30.0) as client:
        response = client.post(f"{base_url}/v1/vendors/resolve", json=payload)

    response.raise_for_status()
    print(json.dumps(response.json(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
