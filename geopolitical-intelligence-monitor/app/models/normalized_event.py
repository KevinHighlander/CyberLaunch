"""Normalized intelligence event model for CLIM."""

from __future__ import annotations

from dataclasses import dataclass

from app.enums.source import SourceAuthority, SourceReliability


@dataclass(frozen=True, slots=True)
class NormalizedEvent:
    """A normalized event ready for intelligence analysis."""

    event_uid: str
    title: str
    summary: str

    source_name: str
    source_url: str
    source_type: str
    source_country: str | None

    source_authority: SourceAuthority
    source_reliability: SourceReliability

    published_at: str | None = None
    region_hint: str | None = None

    @property
    def analysis_text(self) -> str:
        """Return combined text used by the intelligence analyzer."""
        if self.summary.strip():
            return f"{self.title}. {self.summary}"

        return self.title