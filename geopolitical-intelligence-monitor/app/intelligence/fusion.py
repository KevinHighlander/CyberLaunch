"""Multi-source intelligence fusion for CLIM."""

from __future__ import annotations

from dataclasses import dataclass

from app.intelligence.analyzer import AnalysisResult, analyze
from app.intelligence.correlation_groups import (
    CorrelationGroup,
    group_events,
)
from app.models.normalized_event import NormalizedEvent


@dataclass(frozen=True, slots=True)
class FusedEvent:
    """A correlated group of reports with shared intelligence analysis."""

    group: CorrelationGroup
    analysis: AnalysisResult

    @property
    def source_count(self) -> int:
        """Return the number of unique reporting sources."""
        return self.group.source_count

    @property
    def is_corroborated(self) -> bool:
        """Return whether multiple independent sources support the event."""
        return self.group.is_corroborated


def fuse_group(
    group: CorrelationGroup,
) -> FusedEvent:
    """Analyze a correlation group as one fused intelligence event."""
    combined_text = " ".join(
        event.analysis_text
        for event in group.events
    )

    analysis = analyze(
        combined_text,
        corroborating_sources=group.source_count,
    )

    return FusedEvent(
        group=group,
        analysis=analysis,
    )


def fuse_events(
    events: list[NormalizedEvent],
    *,
    threshold: float = 0.40,
) -> tuple[FusedEvent, ...]:
    """Correlate normalized reports and analyze the resulting event groups."""
    groups = group_events(
        events,
        threshold=threshold,
    )

    return tuple(
        fuse_group(group)
        for group in groups
    )