"""Tests for the CLIM RSS collector."""

from app.collectors.rss import (
    clean_text,
    create_event_uid,
)
from app.enums.source import (
    SourceAuthority,
    SourceReliability,
)
from app.models.normalized_event import NormalizedEvent


def test_clean_text_removes_markup() -> None:
    result = clean_text(
        "<p>North Korea <strong>launched</strong> a missile.</p>"
    )

    assert result == "North Korea launched a missile."


def test_event_uid_is_deterministic() -> None:
    first = create_event_uid(
        "https://example.com/story",
        "Test headline",
    )

    second = create_event_uid(
        "https://example.com/story",
        "Test headline",
    )

    assert first == second


def test_normalized_event_supports_source_metadata() -> None:
    event = NormalizedEvent(
        event_uid="123",
        title="Test event",
        summary="Summary",
        source_name="Test Source",
        source_url="https://example.com",
        source_type="media",
        source_country="United States",
        source_authority=SourceAuthority.SECONDARY,
        source_reliability=SourceReliability.HIGH,
    )

    assert event.source_type == "media"
    assert event.source_country == "United States"
    assert event.source_authority is SourceAuthority.SECONDARY
    assert event.source_reliability is SourceReliability.HIGH