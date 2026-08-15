"""Public-source registry for CLIM."""

from __future__ import annotations

from app.enums.source import SourceAuthority, SourceReliability
from app.models.source import IntelligenceSource


SOURCES: tuple[IntelligenceSource, ...] = (
    IntelligenceSource(
        key="bbc-world",
        display_name="BBC World",
        url="https://feeds.bbci.co.uk/news/world/rss.xml",
        source_type="media",
        country="United Kingdom",
        authority=SourceAuthority.SECONDARY,
        reliability=SourceReliability.HIGH,
        region="global",
        collector="rss",
        tags=("world", "general-news"),
    ),
    IntelligenceSource(
        key="bbc-asia",
        display_name="BBC Asia",
        url="https://feeds.bbci.co.uk/news/world/asia/rss.xml",
        source_type="media",
        country="United Kingdom",
        authority=SourceAuthority.SECONDARY,
        reliability=SourceReliability.HIGH,
        region="indo-pacific",
        collector="rss",
        tags=("asia", "indo-pacific"),
    ),
)


def get_enabled_sources(
    collector: str | None = None,
) -> tuple[IntelligenceSource, ...]:
    """Return enabled sources, optionally filtered by collector."""
    sources = tuple(
        source
        for source in SOURCES
        if source.enabled
    )

    if collector is None:
        return sources

    return tuple(
        source
        for source in sources
        if source.supports_collector(collector)
    )


def get_source(key: str) -> IntelligenceSource | None:
    """Return one source by key."""
    return next(
        (
            source
            for source in SOURCES
            if source.key == key
        ),
        None,
    )