"""RSS and Atom collection for CLIM."""

from __future__ import annotations

import hashlib
import re
from html import unescape

import feedparser

from app.models.normalized_event import NormalizedEvent
from app.models.source import IntelligenceSource


class FeedCollectionError(RuntimeError):
    """Raised when an RSS or Atom source cannot be parsed."""


def clean_text(value: str | None) -> str:
    """Remove simple markup and normalize whitespace."""
    if not value:
        return ""

    text = re.sub(r"<[^>]+>", " ", value)
    return " ".join(unescape(text).split())


def create_event_uid(source_url: str, title: str) -> str:
    """Create a deterministic event identifier for deduplication."""
    raw_value = f"{source_url}|{title}".encode("utf-8")
    return hashlib.sha256(raw_value).hexdigest()


def collect_feed(
    source: IntelligenceSource,
) -> list[NormalizedEvent]:
    """Fetch one RSS/Atom source and normalize its entries."""
    feed_url = source.url
    source_name = source.display_name

    feed = feedparser.parse(feed_url)

    if getattr(feed, "bozo", False) and not feed.entries:
        error = getattr(
            feed,
            "bozo_exception",
            "unknown feed error",
        )

        raise FeedCollectionError(
            f"Could not parse {source_name}: {error}"
        )

    events: list[NormalizedEvent] = []

    for entry in feed.entries:
        title = clean_text(
            entry.get("title")
        )

        if not title:
            continue

        source_url = str(
            entry.get(
                "link",
                feed_url,
            )
        )

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

        event = NormalizedEvent(
    event_uid=create_event_uid(
        source_url,
        title,
    ),
    title=title,
    summary=summary,
    source_name=source.display_name,
    source_url=source_url,
    source_type=source.source_type,
    source_country=source.country,
    source_authority=source.authority,
    source_reliability=source.reliability,
    published_at=(
        str(published_at)
        if published_at is not None
        else None
    ),
    region_hint=source.region,
)

        events.append(event)

    return events