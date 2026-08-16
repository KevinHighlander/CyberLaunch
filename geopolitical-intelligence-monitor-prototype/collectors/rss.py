"""RSS collection and normalization for CLIM."""

from __future__ import annotations

import hashlib
import re
from html import unescape
from typing import Any

import feedparser

from intelligence.significance import score_event
from watchlists import classify_watch


def clean_text(value: str | None) -> str:
    """Remove basic HTML markup and normalize whitespace."""
    if not value:
        return ""

    text = re.sub(r"<[^>]+>", " ", value)
    text = unescape(text)
    return " ".join(text.split())


def create_event_uid(source_url: str, title: str) -> str:
    """Create a deterministic identifier for deduplication."""
    raw_value = f"{source_url}|{title}".encode("utf-8")
    return hashlib.sha256(raw_value).hexdigest()


def collect_feed(
    feed_url: str,
    source_name: str,
    region: str = "unclassified",
) -> list[dict[str, Any]]:
    """Fetch an RSS/Atom feed and normalize its entries."""
    feed = feedparser.parse(feed_url)

    if getattr(feed, "bozo", False) and not feed.entries:
        error = getattr(feed, "bozo_exception", "unknown feed error")
        raise RuntimeError(f"Could not parse {source_name}: {error}")

    events: list[dict[str, Any]] = []

    for entry in feed.entries:
        title = clean_text(entry.get("title"))

        if not title:
            continue

        source_url = entry.get("link", feed_url)

        summary = clean_text(
            entry.get("summary")
            or entry.get("description")
            or ""
        )

        published_at = (
            entry.get("published")
            or entry.get("updated")
            or None
        )

        significance = score_event(title, summary)
        watch = classify_watch(title, summary)

        event_region = (
            watch.display_name
            if watch is not None
            else region
        )

        events.append(
            {
                "event_uid": create_event_uid(source_url, title),
                "title": title,
                "summary": summary,
                "source_name": source_name,
                "source_url": source_url,
                "published_at": published_at,
                "region": event_region,
                "category": significance.category,
                "significance": significance.score,
                "confidence": "single-source",
            }
        )

    return events
