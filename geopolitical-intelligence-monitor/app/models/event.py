"""Core intelligence event model for CLIM."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal


SourceAuthority = Literal["primary", "secondary", "unknown"]
SourceReliability = Literal["official", "high", "medium", "low", "unknown"]
ConfidenceLevel = Literal["unrated", "single-source", "low", "medium", "high"]


@dataclass(slots=True)
class IntelligenceEvent:
    """Normalized intelligence event used throughout CLIM."""

    event_uid: str
    title: str
    summary: str
    source_name: str
    source_url: str
    source_type: str
    source_country: str | None
    source_authority: SourceAuthority
    source_reliability: SourceReliability
    published_at: str | None
    region: str = "unclassified"
    category: str = "unclassified"
    significance: int = 0
    confidence: ConfidenceLevel = "unrated"
    collected_at: datetime | None = None

    def __post_init__(self) -> None:
        if self.collected_at is None:
            self.collected_at = datetime.now(timezone.utc)

    def is_significant(self, minimum_score: int = 3) -> bool:
        """Return whether the event meets the requested threshold."""
        return self.significance >= minimum_score

    def short_summary(self, max_length: int = 260) -> str:
        """Return a terminal-friendly summary."""
        text = self.summary.strip()
        if len(text) <= max_length:
            return text
        if max_length <= 3:
            return text[:max_length]
        return f"{text[: max_length - 3].rstrip()}..."
