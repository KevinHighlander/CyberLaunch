"""CLIM command-line application."""

from __future__ import annotations

from datetime import datetime, timezone

from app.collectors.rss import (
    FeedCollectionError,
    collect_feed,
)
from app.config import (
    BRIEF_EVENT_LIMIT,
    SIGNIFICANCE_THRESHOLD,
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
            key=lambda indicator: int(
                indicator.impact
            ),
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
        collected_at=datetime.now(
            timezone.utc
        ),

        region=region,
        category=category,

        significance=int(
            analysis.impact
        ),

        confidence=analysis.confidence.level,
    )


def collect_intelligence(
    repository: EventRepository,
) -> tuple[int, int]:
    """Collect, analyze, and store enabled RSS sources."""
    discovered = 0
    inserted = 0

    for source in get_enabled_sources(
        collector="rss"
    ):
        print(
            f"[COLLECT] {source.display_name}"
        )

        try:
            events = collect_feed(
                source
            )

        except FeedCollectionError as error:
            print(
                f"[ERROR] {error}"
            )
            continue

        discovered += len(events)

        for normalized_event in events:
            analyzed_event = analyze_event(
                normalized_event
            )

            if repository.insert(
                analyzed_event
            ):
                inserted += 1

    return discovered, inserted


def print_brief(
    repository: EventRepository,
) -> None:
    """Print significant stored intelligence events."""
    events = repository.significant(
        minimum_score=SIGNIFICANCE_THRESHOLD,
        limit=BRIEF_EVENT_LIMIT,
    )

    print()
    print("=" * 72)
    print(
        "CYBERLAUNCH INTELLIGENCE MONITOR"
    )
    print(
        "SIGNIFICANT GEOPOLITICAL EVENTS"
    )
    print("=" * 72)

    if not events:
        print(
            "No events currently meet "
            "the significance threshold."
        )

    else:
        for event in events:
            print()

            print(
                f"[{event['region'].upper()}] "
                f"[IMPACT {event['significance']}] "
                f"[{event['category'].upper()}]"
            )

            print(
                event["title"]
            )

            print(
                f"Source: {event['source_name']} | "
                f"{event['source_authority']} | "
                f"{event['source_reliability']}"
            )

            print(
                f"Confidence: "
                f"{event['confidence'].upper()}"
            )

            if event["published_at"]:
                print(
                    f"Published: "
                    f"{event['published_at']}"
                )

            if event["summary"]:
                summary = str(
                    event["summary"]
                )

                if len(summary) > 260:
                    summary = (
                        f"{summary[:257]}..."
                    )

                print(
                    f"Summary: {summary}"
                )

    print()
    print("-" * 72)

    print(
        f"Total raw events stored: "
        f"{repository.count()}"
    )

    print("=" * 72)


def main() -> None:
    """Run one CLIM collection and analysis cycle."""
    repository = EventRepository()

    repository.initialize()

    discovered, inserted = (
        collect_intelligence(
            repository
        )
    )

    print()

    print(
        f"[RESULT] {discovered} "
        "feed entries discovered"
    )

    print(
        f"[RESULT] {inserted} "
        "new intelligence events stored"
    )

    print_brief(
        repository
    )


if __name__ == "__main__":
    main()