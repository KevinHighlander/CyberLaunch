"""Tests for the CLIM normalized event model."""

from app.enums.source import SourceAuthority, SourceReliability
from app.models.normalized_event import NormalizedEvent


def make_event(
    *,
    title: str = "North Korea conducted a ballistic missile launch",
    summary: str = "The missile was launched early Tuesday.",
) -> NormalizedEvent:
    return NormalizedEvent(
        event_uid="event-123",
        title=title,
        summary=summary,
        source_name="Test Source",
        source_url="https://example.com/event",
        source_type="media",
        source_country="United States",
        source_authority=SourceAuthority.SECONDARY,
        source_reliability=SourceReliability.HIGH,
    )


def test_analysis_text_combines_title_and_summary() -> None:
    event = make_event()

    assert event.analysis_text == (
        "North Korea conducted a ballistic missile launch. "
        "The missile was launched early Tuesday."
    )


def test_analysis_text_uses_title_when_summary_is_empty() -> None:
    event = make_event(summary="")

    assert event.analysis_text == (
        "North Korea conducted a ballistic missile launch"
    )


def test_source_metadata_is_preserved() -> None:
    event = make_event()

    assert event.source_type == "media"
    assert event.source_country == "United States"
    assert event.source_authority is SourceAuthority.SECONDARY
    assert event.source_reliability is SourceReliability.HIGH