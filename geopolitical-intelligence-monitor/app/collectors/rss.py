"""RSS and Atom collection for CLIM."""

from __future__ import annotations

import hashlib
import re
from html import unescape

import feedparser

from app.intelligence.significance import score_event
from app.models.event import IntelligenceEvent
from app.watchlists.registry import classify_watch


class FeedCollectionError(RuntimeError):
    """Raised when an RSS/Atom source cannot be parsed."""


def clean_text(value: str | None) -> str:
    """Remove simple markup and normalize whitespace."""
    if not value:
        return ""
    text = re.sub(r"<[^>]+>", " ", value)
    return " ".join(unescape(text).split())


def create_event_uid(source_url: str, title: str) -> str:
    """Create a deterministic event identifier for deduplication."""
    raw = f"{source_url}|{title}".encode()
    return hashlib.sha256(raw).hexdigest()


def collect_feed(source: dict[str, object]) -> list[IntelligenceEvent]:
    """Fetch and normalize one RSS/Atom source."""
    feed_url = str(source["url"])
    source_name = str(source["name"])
    feed = feedparser.parse(feed_url)

    if getattr(feed, "bozo", False) and not feed.entries:
        error = getattr(feed, "bozo_exception", "unknown feed error")
        raise FeedCollectionError(f"Could not parse {source_name}: {error}")

    events: list[IntelligenceEvent] = []

    for entry in feed.entries:
        title = clean_text(entry.get("title"))
        if not title:
            continue

        source_url = str(entry.get("link", feed_url))
        summary = clean_text(entry.get("summary") or entry.get("description") or "")
        published_at = entry.get("published") or entry.get("updated") or None

        significance = score_event(title, summary)
        watch = classify_watch(title, summary)

        events.append(
            IntelligenceEvent(
                event_uid=create_event_uid(source_url, title),
                title=title,
                summary=summary,
                source_name=source_name,
                source_url=source_url,
                source_type=str(source.get("source_type", "unknown")),
                source_country=(
                    str(source["country"]) if source.get("country") is not None else None
                ),
                source_authority=str(source.get("authority", "unknown")),  # type: ignore[arg-type]
                source_reliability=str(source.get("reliability", "unknown")),  # type: ignore[arg-type]
                published_at=str(published_at) if published_at is not None else None,
                region=watch.display_name if watch else str(source.get("region", "unclassified")),
                category=significance.category,
                significance=significance.score,
                confidence="single-source",
            )
        )

    return events
