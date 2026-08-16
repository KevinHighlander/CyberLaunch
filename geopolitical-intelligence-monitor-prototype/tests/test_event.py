"""Tests for the CLIM intelligence event model."""

from app.models.event import IntelligenceEvent


def make_event(significance: int = 0) -> IntelligenceEvent:
    return IntelligenceEvent(
        event_uid="abc123",
        title="Test intelligence event",
        summary="A test summary for CLIM.",
        source_name="Test Source",
        source_url="https://example.com",
        source_type="media",
        source_country="United States",
        source_authority="secondary",
        source_reliability="high",
        published_at=None,
        significance=significance,
    )


def test_event_below_significance_threshold() -> None:
    event = make_event(significance=2)

    assert event.is_significant() is False


def test_event_meets_significance_threshold() -> None:
    event = make_event(significance=3)

    assert event.is_significant() is True


def test_short_summary_truncates_long_text() -> None:
    event = make_event()
    event.summary = "A" * 300

    result = event.short_summary(max_length=50)

    assert len(result) == 50
    assert result.endswith("...")