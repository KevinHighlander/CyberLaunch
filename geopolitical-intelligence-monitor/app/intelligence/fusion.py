"""Multi-source intelligence fusion for CLIM."""

from __future__ import annotations

from dataclasses import dataclass

from app.intelligence.analyzer import AnalysisResult, analyze
from app.intelligence.confidence import assess_fused_confidence
from app.intelligence.correlation_groups import (
    CorrelationGroup,
    group_events,
)
from app.intelligence.knowledge_graph import (
    KnowledgeGraph,
    KnowledgeNeighborhood,
)
from app.intelligence.source_diversity import (
    SourceDiversityResult,
    assess_event_source_diversity,
)
from app.models.normalized_event import NormalizedEvent


_KNOWLEDGE_GRAPH = KnowledgeGraph()


@dataclass(frozen=True, slots=True)
class FusedEvent:
    """A correlated group of reports with shared intelligence analysis."""

    group: CorrelationGroup
    analysis: AnalysisResult
    source_diversity: SourceDiversityResult
    knowledge_neighborhoods: tuple[KnowledgeNeighborhood, ...]

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
    """Analyze and enrich one correlated intelligence event."""
    combined_text = " ".join(
        event.analysis_text
        for event in group.events
    )

    analysis = analyze(
        combined_text,
        corroborating_sources=group.source_count,
    )

    fused_confidence = assess_fused_confidence(
        group.events
    )

    analysis = AnalysisResult(
        text=analysis.text,
        entities=analysis.entities,
        indicators=analysis.indicators,
        theaters=analysis.theaters,
        impact=analysis.impact,
        escalation=analysis.escalation,
        context=analysis.context,
        reasoning=analysis.reasoning,
        confidence=fused_confidence,
    )

    source_diversity = assess_event_source_diversity(
        group.events
    )

    knowledge_neighborhoods = _KNOWLEDGE_GRAPH.snapshot(
        tuple(
            entity.key
            for entity in analysis.entities
        )
    )

    return FusedEvent(
        group=group,
        analysis=analysis,
        source_diversity=source_diversity,
        knowledge_neighborhoods=knowledge_neighborhoods,
    )


def fuse_events(
    events: list[NormalizedEvent],
    *,
    threshold: float = 0.40,
) -> tuple[FusedEvent, ...]:
    """Correlate reports and analyze the resulting event groups."""
    groups = group_events(
        events,
        threshold=threshold,
    )

    return tuple(
        fuse_group(group)
        for group in groups
    )