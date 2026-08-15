"""Integration tests for CLIM normalization-to-analysis flow."""

from app.enums.confidence import Confidence
from app.enums.source import (
    SourceAuthority,
    SourceReliability,
)
from app.main import analyze_event
from app.models.normalized_event import NormalizedEvent


def make_normalized_event() -> NormalizedEvent:
    """Return a normalized missile-launch report."""
    return NormalizedEvent(
        event_uid="normalized-1",

        title=(
            "North Korea conducted "
            "a ballistic missile launch"
        ),

        summary=(
            "Officials reported the launch "
            "early Tuesday."
        ),

        source_name="Test Source",

        source_url=(
            "https://example.com/report"
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
        region_hint="indo-pacific",
    )


def test_normalized_event_becomes_analyzed_event() -> None:
    result = analyze_event(
        make_normalized_event()
    )

    assert result.category == "military"

    assert result.region == "Indo-Pacific"

    assert result.significance == 5


def test_analysis_preserves_source_metadata() -> None:
    result = analyze_event(
        make_normalized_event()
    )

    assert (
        result.source_authority
        is SourceAuthority.SECONDARY
    )

    assert (
        result.source_reliability
        is SourceReliability.HIGH
    )


def test_analysis_produces_confidence() -> None:
    result = analyze_event(
        make_normalized_event()
    )

    assert result.confidence in {
        Confidence.UNRATED,
        Confidence.LOW,
        Confidence.MEDIUM,
        Confidence.HIGH,
        Confidence.VERY_HIGH,
    }