"""CLIM collection and analysis orchestration."""

from __future__ import annotations

from datetime import datetime, timezone

from app.collectors.rss import (
    FeedCollectionError,
    collect_feed,
)
from app.intelligence.analyzer import analyze
from app.models.analyzed_event import AnalyzedEvent
from app.models.normalized_event import NormalizedEvent
from app.sources import get_enabled_sources
from app.storage.database import EventRepository


def analyze_event(
    event: NormalizedEvent,
) -> AnalyzedEvent:
    """Convert a normalized report into a persistable analyzed event."""
    analysis = analyze(
        event.analysis_text,
        authority=event.source_authority,
        reliability=event.source_reliability,
        corroborating_sources=1,
    )

    if analysis.theaters:
        region = analysis.theaters[0].display_name
    elif event.region_hint:
        region = event.region_hint
    else:
        region = "unclassified"

    if analysis.indicators:
        highest_indicator = max(
            analysis.indicators,
            key=lambda indicator: int(indicator.impact),
        )
        category = highest_indicator.category
    else:
        category = "general"

    return AnalyzedEvent(
        event_uid=event.event_uid,
        title=event.title,
        summary=event.summary,
        source_name=event.source_name,
        source_url=event.source_url,
        source_type=event.source_type,
        source_country=event.source_country,
        source_authority=event.source_authority,
        source_reliability=event.source_reliability,
        published_at=event.published_at,
        collected_at=datetime.now(timezone.utc),
        region=region,
        category=category,
        significance=int(analysis.impact),
        confidence=analysis.confidence.level,
    )


def collect_intelligence(
    repository: EventRepository,
) -> tuple[int, int]:
    """Collect, analyze, and store enabled RSS sources."""
    discovered = 0
    inserted = 0

    for source in get_enabled_sources(collector="rss"):
        print(f"[COLLECT] {source.display_name}")

        try:
            events = collect_feed(source)
        except FeedCollectionError as error:
            print(f"[ERROR] {error}")
            continue

        discovered += len(events)

        for normalized_event in events:
            analyzed_event = analyze_event(normalized_event)

            if repository.insert(analyzed_event):
                inserted += 1

    return discovered, inserted