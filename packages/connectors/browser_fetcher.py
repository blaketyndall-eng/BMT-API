from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from html import unescape

import httpx

TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)
SCRIPT_STYLE_RE = re.compile(r"<(script|style)[^>]*>.*?</\\1>", re.IGNORECASE | re.DOTALL)
TAG_RE = re.compile(r"<[^>]+>")
WHITESPACE_RE = re.compile(r"\s+")


@dataclass(frozen=True)
class BrowserFetchResult:
    requested_url: str
    final_url: str
    status_code: int
    content_type: str | None
    title: str | None
    page_text: str | None
    content_sha256: str
    fetched_at: datetime


def extract_title(html: str) -> str | None:
    match = TITLE_RE.search(html)
    if match is None:
        return None
    title = unescape(match.group(1)).strip()
    title = WHITESPACE_RE.sub(" ", title)
    return title or None


def html_to_text(html: str) -> str:
    without_scripts = SCRIPT_STYLE_RE.sub(" ", html)
    without_tags = TAG_RE.sub(" ", without_scripts)
    plain_text = unescape(without_tags)
    plain_text = WHITESPACE_RE.sub(" ", plain_text).strip()
    return plain_text


async def fetch_page(url: str) -> BrowserFetchResult:
    async with httpx.AsyncClient(
        follow_redirects=True,
        timeout=20.0,
        headers={"User-Agent": "BMT-API/0.1 (+https://github.com/blaketyndall-eng/BMT-API)"},
    ) as client:
        response = await client.get(url)

    content_type = response.headers.get("content-type")
    text_body = response.text
    page_text = html_to_text(text_body)[:20000] if text_body else None

    return BrowserFetchResult(
        requested_url=url,
        final_url=str(response.url),
        status_code=response.status_code,
        content_type=content_type,
        title=extract_title(text_body),
        page_text=page_text,
        content_sha256=hashlib.sha256(response.content).hexdigest(),
        fetched_at=datetime.now(timezone.utc),
    )
