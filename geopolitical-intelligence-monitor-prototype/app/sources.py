"""Source registry for CyberLaunch Intelligence Monitor."""

from __future__ import annotations

SOURCES = [
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
    {
        "id": "japan-mod-press",
        "name": "Japan Ministry of Defense",
        "url": "https://www.mod.go.jp/j/rss/news.xml",
        "source_type": "government",
        "country": "Japan",
        "authority": "primary",
        "reliability": "official",
        "region": "indo-pacific",
        "collector": "rss",
        "enabled": True,
    },
    {
        "id": "japan-mod-updates",
        "name": "Japan Ministry of Defense Updates",
        "url": "https://www.mod.go.jp/j/rss/update.xml",
        "source_type": "government",
        "country": "Japan",
        "authority": "primary",
        "reliability": "official",
        "region": "indo-pacific",
        "collector": "rss",
        "enabled": True,
    },
]


def get_enabled_sources() -> list[dict[str, object]]:
    """Return currently enabled CLIM sources."""
    return [
        source
        for source in SOURCES
        if source.get("enabled", False)
    ]
