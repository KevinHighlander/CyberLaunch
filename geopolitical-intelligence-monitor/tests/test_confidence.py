"""Tests for CLIM confidence assessment."""

from app.enums.confidence import Confidence
from app.enums.source import SourceAuthority, SourceReliability
from app.intelligence.confidence import assess_confidence


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