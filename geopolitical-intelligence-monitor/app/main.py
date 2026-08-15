"""CLIM command-line entry point."""

from __future__ import annotations

from app.collectors.rss import FeedCollectionError, collect_feed
from app.config import BRIEF_EVENT_LIMIT, SIGNIFICANCE_THRESHOLD
from app.sources import get_enabled_sources
from app.storage.database import EventRepository


def collect_intelligence(repository: EventRepository) -> tuple[int, int]:
    discovered = 0
    inserted = 0

    for source in get_enabled_sources(collector="rss"):
        print(f"[COLLECT] {source['name']}")
        try:
            events = collect_feed(source)
        except FeedCollectionError as error:
            print(f"[ERROR] {error}")
            continue

        discovered += len(events)
        for event in events:
            if repository.insert(event):
                inserted += 1

    return discovered, inserted


def print_brief(repository: EventRepository) -> None:
    events = repository.significant(
        minimum_score=SIGNIFICANCE_THRESHOLD,
        limit=BRIEF_EVENT_LIMIT,
    )

    print()
    print("=" * 72)
    print("CYBERLAUNCH INTELLIGENCE MONITOR")
    print("SIGNIFICANT GEOPOLITICAL EVENTS")
    print("=" * 72)

    if not events:
        print("No events currently meet the significance threshold.")
    else:
        for event in events:
            print()
            print(
                f"[{event['region'].upper()}] "
                f"[SCORE {event['significance']}] "
                f"[{event['category'].upper()}]"
            )
            print(event["title"])
            print(
                f"Source: {event['source_name']} | "
                f"{event['source_authority']} | "
                f"{event['source_reliability']}"
            )
            if event["published_at"]:
                print(f"Published: {event['published_at']}")
            if event["summary"]:
                summary = str(event["summary"])
                print(f"Summary: {summary[:257] + '...' if len(summary) > 260 else summary}")

    print()
    print("-" * 72)
    print(f"Total raw events stored: {repository.count()}")
    print("=" * 72)


def main() -> None:
    repository = EventRepository()
    repository.initialize()

    discovered, inserted = collect_intelligence(repository)
    print()
    print(f"[RESULT] {discovered} feed entries discovered")
    print(f"[RESULT] {inserted} new intelligence events stored")

    print_brief(repository)


if __name__ == "__main__":
    main()
