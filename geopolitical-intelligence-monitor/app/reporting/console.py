"""Console reporting for stored CLIM intelligence events."""

from __future__ import annotations

from app.config import (
    BRIEF_EVENT_LIMIT,
    SIGNIFICANCE_THRESHOLD,
)
from app.storage.database import EventRepository


def print_event_listing(
    repository: EventRepository,
) -> None:
    """Print significant stored intelligence events."""
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

            print(event["title"])

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
                summary = str(event["summary"])

                if len(summary) > 260:
                    summary = f"{summary[:257]}..."

                print(f"Summary: {summary}")

    print()
    print("-" * 72)

    print(
        f"Total raw events stored: "
        f"{repository.count()}"
    )

    print("=" * 72)