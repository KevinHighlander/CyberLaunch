"""Tests for reconstructed normalized evidence from event storage."""

from datetime import datetime, timezone
from pathlib import Path

from app.enums.confidence import Confidence
from app.enums.source import (
    SourceAuthority,
    SourceReliability,
)
from app.models.analyzed_event import AnalyzedEvent
from app.storage.database import EventRepository


def make_event(
    event_uid: str = "event-1",
) -> AnalyzedEvent:
    """Create deterministic analyzed evidence for repository tests."""
    return AnalyzedEvent(
        event_uid=event_uid,
        title=(
            "China launches military exercises "
            "around Taiwan"
        ),
        summary=(
            "Military activity was reported "
            "near Taiwan."
        ),
        source_name="Reuters",
        source_url=(
            f"https://example.com/{event_uid}"
        ),
        source_type="media",
        source_country="United Kingdom",
        source_authority=(
            SourceAuthority.SECONDARY
        ),
        source_reliability=(
            SourceReliability.HIGH
        ),
        published_at=(
            "2026-08-26T12:00:00+00:00"
        ),
        collected_at=datetime(
            2026,
            8,
            26,
            12,
            5,
            tzinfo=timezone.utc,
        ),
        region="Indo-Pacific",
        category="military",
        significance=3,
        confidence=Confidence.MEDIUM,
    )


def test_get_normalized_reconstructs_stored_event(
    tmp_path: Path,
) -> None:
    repository = EventRepository(
        tmp_path / "clim.db"
    )

    repository.initialize()

    repository.insert(
        make_event()
    )

    normalized = repository.get_normalized(
        "event-1"
    )

    assert normalized is not None

    assert normalized.event_uid == "event-1"

    assert normalized.title == (
        "China launches military exercises "
        "around Taiwan"
    )

    assert normalized.summary == (
        "Military activity was reported "
        "near Taiwan."
    )

    assert normalized.source_name == "Reuters"

    assert normalized.source_authority == (
        SourceAuthority.SECONDARY
    )

    assert normalized.source_reliability == (
        SourceReliability.HIGH
    )

    assert normalized.region_hint is None


def test_get_normalized_returns_none_for_missing_event(
    tmp_path: Path,
) -> None:
    repository = EventRepository(
        tmp_path / "clim.db"
    )

    repository.initialize()

    assert repository.get_normalized(
        "missing-event"
    ) is None


def test_get_normalized_many_returns_requested_events(
    tmp_path: Path,
) -> None:
    repository = EventRepository(
        tmp_path / "clim.db"
    )

    repository.initialize()

    repository.insert(
        make_event(
            "event-1"
        )
    )

    repository.insert(
        make_event(
            "event-2"
        )
    )

    evidence = repository.get_normalized_many(
        (
            "event-1",
            "event-2",
        )
    )

    assert set(
        evidence
    ) == {
        "event-1",
        "event-2",
    }

    assert (
        evidence["event-1"].source_name
        == "Reuters"
    )

    assert (
        evidence["event-2"].source_name
        == "Reuters"
    )


def test_get_normalized_many_ignores_missing_events(
    tmp_path: Path,
) -> None:
    repository = EventRepository(
        tmp_path / "clim.db"
    )

    repository.initialize()

    repository.insert(
        make_event(
            "event-1"
        )
    )

    evidence = repository.get_normalized_many(
        (
            "event-1",
            "missing-event",
        )
    )

    assert set(
        evidence
    ) == {
        "event-1",
    }


def test_get_normalized_many_handles_empty_input(
    tmp_path: Path,
) -> None:
    repository = EventRepository(
        tmp_path / "clim.db"
    )

    repository.initialize()

    evidence = repository.get_normalized_many(
        ()
    )

    assert evidence == {}


def test_reconstructed_analysis_text_is_available(
    tmp_path: Path,
) -> None:
    repository = EventRepository(
        tmp_path / "clim.db"
    )

    repository.initialize()

    repository.insert(
        make_event()
    )

    normalized = repository.get_normalized(
        "event-1"
    )

    assert normalized is not None

    assert normalized.analysis_text == (
        "China launches military exercises "
        "around Taiwan. "
        "Military activity was reported "
        "near Taiwan."
    )