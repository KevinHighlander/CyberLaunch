"""Tests for CLIM confidence assessment."""

from app.enums.confidence import Confidence
from app.enums.source import SourceAuthority, SourceReliability
from app.intelligence.confidence import (
    assess_confidence,
    assess_fused_confidence,
)


def test_primary_official_with_multiple_sources_is_very_high() -> None:
    result = assess_confidence(
        authority=SourceAuthority.PRIMARY,
        reliability=SourceReliability.OFFICIAL,
        corroborating_sources=3,
    )

    assert result.level is Confidence.VERY_HIGH
    assert result.score >= 85


def test_single_high_quality_secondary_source_is_medium() -> None:
    result = assess_confidence(
        authority=SourceAuthority.SECONDARY,
        reliability=SourceReliability.HIGH,
        corroborating_sources=1,
    )

    assert result.level is Confidence.MEDIUM


def test_unknown_single_source_is_unrated_or_low() -> None:
    result = assess_confidence(
        authority=SourceAuthority.UNKNOWN,
        reliability=SourceReliability.UNKNOWN,
        corroborating_sources=1,
    )

    assert result.level in {
        Confidence.UNRATED,
        Confidence.LOW,
    }


def test_more_corroboration_increases_confidence() -> None:
    one_source = assess_confidence(
        authority=SourceAuthority.SECONDARY,
        reliability=SourceReliability.HIGH,
        corroborating_sources=1,
    )

    three_sources = assess_confidence(
        authority=SourceAuthority.SECONDARY,
        reliability=SourceReliability.HIGH,
        corroborating_sources=3,
    )

    assert three_sources.score > one_source.score


def test_confidence_includes_reasoning() -> None:
    result = assess_confidence(
        authority=SourceAuthority.PRIMARY,
        reliability=SourceReliability.OFFICIAL,
        corroborating_sources=2,
    )

    assert any(
        reason.startswith("Source authority:")
        for reason in result.reasons
    )

    assert any(
        reason.startswith("Confidence result:")
        for reason in result.reasons
    )

def test_fused_confidence_uses_source_provenance() -> None:
    from app.models.normalized_event import NormalizedEvent

    events = (
        NormalizedEvent(
            event_uid="reuters-1",
            title="Test event",
            summary="",
            source_name="Reuters",
            source_url="https://example.com/reuters",
            source_type="media",
            source_country="United Kingdom",
            source_authority=SourceAuthority.SECONDARY,
            source_reliability=SourceReliability.HIGH,
        ),
        NormalizedEvent(
            event_uid="bbc-1",
            title="Test event",
            summary="",
            source_name="BBC",
            source_url="https://example.com/bbc",
            source_type="media",
            source_country="United Kingdom",
            source_authority=SourceAuthority.SECONDARY,
            source_reliability=SourceReliability.HIGH,
        ),
    )

    result = assess_fused_confidence(
        events
    )

    assert result.score == 65
    assert result.level is Confidence.HIGH


def test_fused_confidence_does_not_use_only_best_source() -> None:
    from app.models.normalized_event import NormalizedEvent

    events = (
        NormalizedEvent(
            event_uid="high-1",
            title="Test event",
            summary="",
            source_name="High Source",
            source_url="https://example.com/high",
            source_type="media",
            source_country=None,
            source_authority=SourceAuthority.SECONDARY,
            source_reliability=SourceReliability.HIGH,
        ),
        NormalizedEvent(
            event_uid="low-1",
            title="Test event",
            summary="",
            source_name="Low Source",
            source_url="https://example.com/low",
            source_type="media",
            source_country=None,
            source_authority=SourceAuthority.SECONDARY,
            source_reliability=SourceReliability.LOW,
        ),
    )

    result = assess_fused_confidence(
        events
    )

    assert result.score == 55
    assert result.level is Confidence.MEDIUM


def test_duplicate_source_does_not_inflate_fused_confidence() -> None:
    from app.models.normalized_event import NormalizedEvent

    events = (
        NormalizedEvent(
            event_uid="reuters-1",
            title="First report",
            summary="",
            source_name="Reuters",
            source_url="https://example.com/1",
            source_type="media",
            source_country=None,
            source_authority=SourceAuthority.SECONDARY,
            source_reliability=SourceReliability.HIGH,
        ),
        NormalizedEvent(
            event_uid="reuters-2",
            title="Second report",
            summary="",
            source_name="Reuters",
            source_url="https://example.com/2",
            source_type="media",
            source_country=None,
            source_authority=SourceAuthority.SECONDARY,
            source_reliability=SourceReliability.HIGH,
        ),
    )

    result = assess_fused_confidence(
        events
    )

    assert result.score == 50
    assert any(
        "did not increase corroboration"
        in reason
        for reason in result.reasons
    )