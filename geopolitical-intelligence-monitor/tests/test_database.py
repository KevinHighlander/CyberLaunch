"""Tests for CLIM analyzed-event persistence."""

from datetime import datetime, timezone
from pathlib import Path

from app.enums.confidence import Confidence
from app.enums.source import (
    SourceAuthority,
    SourceReliability,
)
from app.models.analyzed_event import AnalyzedEvent
from app.storage.database import EventRepository


def make_event() -> AnalyzedEvent:
    """Return a test analyzed intelligence event."""
    return AnalyzedEvent(
        event_uid="event-1",

        title=(
            "North Korea conducts "
            "ballistic missile launch"
        ),

        summary="Test intelligence event.",

        source_name="Test Source",
        source_url=(
            "https://example.com/event-1"
        ),

        source_type="media",
        source_country="United States",

        source_authority=(
            SourceAuthority.SECONDARY
        ),

        source_reliability=(
            SourceReliability.HIGH
        ),

        published_at=None,

        collected_at=datetime.now(
            timezone.utc
        ),

        region="Indo-Pacific",
        category="military",

        significance=5,

        confidence=Confidence.MEDIUM,
    )


def test_repository_deduplicates_events(
    tmp_path: Path,
) -> None:
    repository = EventRepository(
        tmp_path / "clim.db"
    )

    repository.initialize()

    event = make_event()

    assert repository.insert(
        event
    ) is True

    assert repository.insert(
        event
    ) is False

    assert repository.count() == 1


def test_repository_returns_significant_events(
    tmp_path: Path,
) -> None:
    repository = EventRepository(
        tmp_path / "clim.db"
    )

    repository.initialize()

    repository.insert(
        make_event()
    )

    results = repository.significant(
        minimum_score=3,
        limit=10,
    )

    assert len(results) == 1

    assert (
        results[0]["region"]
        == "Indo-Pacific"
    )

    assert (
        results[0]["confidence"]
        == "medium"
    )