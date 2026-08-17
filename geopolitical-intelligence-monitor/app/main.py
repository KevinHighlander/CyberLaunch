"""CLIM command-line application."""

from __future__ import annotations

from app.config import (
    BRIEF_EVENT_LIMIT,
    SIGNIFICANCE_THRESHOLD,
)
from app.intelligence.pipeline import collect_intelligence_run
from app.reporting.brief import build_brief
from app.reporting.console import print_event_listing
from app.storage.database import EventRepository


def main() -> None:
    """Run one CLIM collection and analysis cycle."""
    repository = EventRepository()
    repository.initialize()

    result = collect_intelligence_run(
        repository
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

    significant_analyses = sorted(
        (
            analysis
            for analysis in result.analyses
            if int(analysis.impact)
            >= SIGNIFICANCE_THRESHOLD
        ),
        key=lambda analysis: int(
            analysis.impact
        ),
        reverse=True,
    )[:BRIEF_EVENT_LIMIT]

    for analysis in significant_analyses:
        print()
        print(
            build_brief(
                analysis
            )
        )

    print_event_listing(
        repository
    )


if __name__ == "__main__":
    main()