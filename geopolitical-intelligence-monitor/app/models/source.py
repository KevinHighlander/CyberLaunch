"""Typed intelligence source model for CLIM."""

from __future__ import annotations

from dataclasses import dataclass

from app.enums.source import SourceAuthority, SourceReliability


@dataclass(frozen=True, slots=True)
class IntelligenceSource:
    """A public information source monitored by CLIM."""

    key: str
    display_name: str
    url: str
    source_type: str
    country: str | None
    authority: SourceAuthority
    reliability: SourceReliability
    region: str
    collector: str
    enabled: bool = True
    tags: tuple[str, ...] = ()

    def supports_collector(self, collector: str) -> bool:
        """Return whether this source uses the requested collector."""
        return self.collector == collector