"""Public-source registry for CLIM."""

from __future__ import annotations

SOURCES: tuple[dict[str, object], ...] = (
    {
        "id": "bbc-world",
        "name": "BBC World",
        "url": "https://feeds.bbci.co.uk/news/world/rss.xml",
        "source_type": "media",
        "country": "United Kingdom",
        "authority": "secondary",
        "reliability": "high",
        "region": "global",
        "collector": "rss",
        "enabled": True,
    },
    {
        "id": "bbc-asia",
        "name": "BBC Asia",
        "url": "https://feeds.bbci.co.uk/news/world/asia/rss.xml",
        "source_type": "media",
        "country": "United Kingdom",
        "authority": "secondary",
        "reliability": "high",
        "region": "indo-pacific",
        "collector": "rss",
        "enabled": True,
    },
)


def get_enabled_sources(collector: str | None = None) -> list[dict[str, object]]:
    """Return enabled sources, optionally filtered by collector type."""
    results = [source for source in SOURCES if source.get("enabled") is True]
    if collector is not None:
        results = [source for source in results if source.get("collector") == collector]
    return results
