"""CLIM command-line application."""

from __future__ import annotations

from app.intelligence.pipeline import collect_intelligence
from app.reporting.console import print_brief
from app.storage.database import EventRepository


def main() -> None:
    """Run one CLIM collection and analysis cycle."""
    repository = EventRepository()
    repository.initialize()

    discovered, inserted = collect_intelligence(
        repository
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

    print_brief(repository)


if __name__ == "__main__":
    main()