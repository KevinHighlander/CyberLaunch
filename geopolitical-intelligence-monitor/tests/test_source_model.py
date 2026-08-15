"""Tests for typed CLIM intelligence sources."""

from app.enums.source import SourceAuthority, SourceReliability
from app.models.source import IntelligenceSource
from app.sources import get_enabled_sources, get_source


def test_source_model_preserves_metadata() -> None:
    source = IntelligenceSource(
        key="test-source",
        display_name="Test Source",
        url="https://example.com/feed.xml",
        source_type="media",
        country="United States",
        authority=SourceAuthority.SECONDARY,
        reliability=SourceReliability.HIGH,
        region="global",
        collector="rss",
        tags=("test",),
    )

    assert source.authority is SourceAuthority.SECONDARY
    assert source.reliability is SourceReliability.HIGH
    assert source.supports_collector("rss") is True


def test_bbc_asia_source_exists() -> None:
    source = get_source("bbc-asia")

    assert source is not None
    assert source.display_name == "BBC Asia"
    assert source.region == "indo-pacific"


def test_enabled_rss_sources_are_typed() -> None:
    sources = get_enabled_sources("rss")

    assert len(sources) >= 2
    assert all(
        isinstance(source, IntelligenceSource)
        for source in sources
    )


def test_unknown_source_returns_none() -> None:
    assert get_source("does-not-exist") is None