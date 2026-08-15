"""Tests for CLIM SQLite storage."""

from pathlib import Path

from app.models.event import IntelligenceEvent
from app.storage.database import EventRepository


def make_event() -> IntelligenceEvent:
    return IntelligenceEvent(
        event_uid="event-1",
        title="North Korea conducts ballistic missile launch",
        summary="Test event",
        source_name="Test Source",
        source_url="https://example.com/event-1",
        source_type="media",
        source_country="United States",
        source_authority="secondary",
        source_reliability="high",
        published_at=None,
        region="Korean Peninsula",
        category="military",
        significance=10,
        confidence="single-source",
    )


def test_repository_deduplicates_events(tmp_path: Path) -> None:
    repository = EventRepository(tmp_path / "clim.db")
    repository.initialize()

    event = make_event()

    assert repository.insert(event) is True
    assert repository.insert(event) is False
    assert repository.count() == 1


def test_repository_returns_significant_events(tmp_path: Path) -> None:
    repository = EventRepository(tmp_path / "clim.db")
    repository.initialize()
    repository.insert(make_event())

    results = repository.significant(minimum_score=3, limit=10)

    assert len(results) == 1
    assert results[0]["region"] == "Korean Peninsula"
