"""Persistable analyzed intelligence event for CLIM."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from app.enums.confidence import Confidence
from app.enums.source import SourceAuthority, SourceReliability


@dataclass(frozen=True, slots=True)
class AnalyzedEvent:
    """Normalized event enriched with CLIM intelligence analysis."""

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
    collected_at: datetime

    region: str
    category: str
    significance: int
    confidence: Confidence