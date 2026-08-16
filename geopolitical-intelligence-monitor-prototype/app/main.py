"""CyberLaunch Intelligence Monitor - Build 1."""

from __future__ import annotations

from app.config import FEEDS
from collectors.rss import collect_feed
from database.db import (
    get_event_count,
    get_significant_events,
    initialize_database,
    insert_event,
)


def collect_intelligence() -> tuple[int, int]:
    """Collect configured feeds and persist newly discovered events."""
    discovered = 0
    inserted = 0

    for source in FEEDS:
        print(f"[COLLECT] {source['name']}")

        try:
            events = collect_feed(
                feed_url=source["url"],
                source_name=source["name"],
                region=source["region"],
            )

        except RuntimeError as error:
            print(f"[ERROR] {source['name']}: {error}")
            continue

        discovered += len(events)

        for event in events:
            if insert_event(event):
                inserted += 1

    return discovered, inserted


def print_brief(limit: int = 10) -> None:
    """Print a significance-filtered intelligence brief."""
    events = get_significant_events(limit=limit)

    print()
    print("=" * 72)
    print("CYBERLAUNCH INTELLIGENCE MONITOR")
    print("SIGNIFICANT GEOPOLITICAL EVENTS")
    print("=" * 72)

    if not events:
        print()
        print("No events currently meet the geopolitical significance threshold.")
        print()
        print("-" * 72)
        print(f"Total raw events stored: {get_event_count()}")
        print("=" * 72)
        return

    for event in events:
        print()
        print(
            f"[{event['region'].upper()}] "
            f"[SCORE {event['significance']}] "
            f"[{event['category'].upper()}]"
        )

        print(event["title"])
        print(f"Source: {event['source_name']}")

        if event["published_at"]:
            print(f"Published: {event['published_at']}")

        if event["summary"]:
            summary = event["summary"]

            if len(summary) > 260:
                summary = f"{summary[:257]}..."

            print(f"Summary: {summary}")

    print()
    print("-" * 72)
    print(f"Total raw events stored: {get_event_count()}")
    print("=" * 72)


def main() -> None:
    """Run one CLIM collection cycle."""
    initialize_database()

    discovered, inserted = collect_intelligence()

    print()
    print(f"[RESULT] {discovered} feed entries discovered")
    print(f"[RESULT] {inserted} new intelligence events stored")

    print_brief()


if __name__ == "__main__":
    main()
