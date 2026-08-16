"""Tests for CLIM source diversity assessment."""

from app.enums.source import SourceAuthority, SourceReliability
from app.intelligence.source_diversity import assess_source_diversity
from app.models.source import IntelligenceSource


def make_source(
    key: str,
    *,
    country: str | None,
    source_type: str,
) -> IntelligenceSource:
    return IntelligenceSource(
        key=key,
        display_name=key,
        url=f"https://example.com/{key}",
        source_type=source_type,
        country=country,
        authority=SourceAuthority.SECONDARY,
        reliability=SourceReliability.HIGH,
        region="global",
        collector="rss",
    )


def test_single_source_has_low_diversity() -> None:
    result = assess_source_diversity(
        (
            make_source(
                "reuters",
                country="United Kingdom",
                source_type="media",
            ),
        )
    )

    assert result.unique_sources == 1
    assert result.diversity_score < 50


def test_multiple_media_sources_increase_diversity() -> None:
    result = assess_source_diversity(
        (
            make_source(
                "reuters",
                country="United Kingdom",
                source_type="media",
            ),
            make_source(
                "bbc",
                country="United Kingdom",
                source_type="media",
            ),
            make_source(
                "nhk",
                country="Japan",
                source_type="media",
            ),
        )
    )

    assert result.unique_sources == 3
    assert result.unique_countries == 2
    assert result.diversity_score >= 60


def test_mixed_source_types_have_higher_diversity() -> None:
    result = assess_source_diversity(
        (
            make_source(
                "reuters",
                country="United Kingdom",
                source_type="media",
            ),
            make_source(
                "taiwan-mod",
                country="Taiwan",
                source_type="government",
            ),
            make_source(
                "usindopacom",
                country="United States",
                source_type="military",
            ),
        )
    )

    assert result.unique_source_types == 3
    assert result.diversity_score >= 90


def test_duplicate_source_does_not_inflate_diversity() -> None:
    source = make_source(
        "reuters",
        country="United Kingdom",
        source_type="media",
    )

    result = assess_source_diversity(
        (
            source,
            source,
            source,
        )
    )

    assert result.unique_sources == 1