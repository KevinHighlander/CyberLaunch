"""CLIM command-line application."""

from __future__ import annotations

from app.config import (
    BRIEF_EVENT_LIMIT,
    SIGNIFICANCE_THRESHOLD,
)
from app.intelligence.fusion import fuse_events
from app.intelligence.pipeline import collect_intelligence_run
from app.reporting.brief import build_fused_brief
from app.reporting.console import print_event_listing
from app.storage.database import EventRepository


def main() -> None:
    """Run one CLIM collection, fusion, and analysis cycle."""
    repository = EventRepository()
    repository.initialize()

    result = collect_intelligence_run(
        repository
    )

    for notice in result.notices:
        if notice.level == "collect":
            print(
                f"[COLLECT] {notice.source_name}"
            )
        elif notice.level == "error":
            print(
                f"[ERROR] {notice.message}"
            )

    print()
    print(
        f"[RESULT] {result.discovered} "
        "feed entries discovered"
    )
    print(
        f"[RESULT] {result.inserted} "
        "new intelligence events stored"
    )

    fused_events = fuse_events(
        list(result.new_events)
    )

    significant_fused_events = sorted(
        (
            fused_event
            for fused_event in fused_events
            if int(
                fused_event.analysis.impact
            )
            >= SIGNIFICANCE_THRESHOLD
        ),
        key=lambda fused_event: int(
            fused_event.analysis.impact
        ),
        reverse=True,
    )[:BRIEF_EVENT_LIMIT]

    for fused_event in significant_fused_events:
        print()
        print(
            build_fused_brief(
                fused_event
            )
        )

    print_event_listing(
        repository
    )


if __name__ == "__main__":
    main()