"""Application entry point for CLIM."""

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
from app.storage.incident_repository import IncidentRepository


def main() -> None:
    """Run one CLIM intelligence collection cycle."""
    repository = EventRepository()
    repository.initialize()

    incident_repository = IncidentRepository(
        repository.database_path
    )
    incident_repository.initialize()

    result = collect_intelligence_run(
        repository,
        incident_repository,
    )

    for notice in result.notices:
        prefix = (
            "[COLLECT]"
            if notice.level == "collect"
            else "[ERROR]"
        )

        print(
            f"{prefix} "
            f"{notice.source_name}: "
            f"{notice.message}"
        )

    print()
    print(
        f"Discovered: {result.discovered}"
    )
    print(
        f"Inserted: {result.inserted}"
    )
    print(
        "Incident Updates: "
        f"{len(result.incident_updates)}"
    )
    print(
        "Known Incidents: "
        f"{incident_repository.count()}"
    )

    fused_events = fuse_events(
        list(
            result.new_events
        )
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
    )[
        :BRIEF_EVENT_LIMIT
    ]

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