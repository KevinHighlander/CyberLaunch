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
    summary: str
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


def _build_fused_summary(
    group: CorrelationGroup,
    analysis: AnalysisResult,
) -> str:
    """Build a concise deterministic summary of a fused event."""
    report_word = (
        "report"
        if group.event_count == 1
        else "reports"
    )

    source_word = (
        "source"
        if group.source_count == 1
        else "independent sources"
    )

    if analysis.indicators:
        event_description = ", ".join(
            indicator.display_name
            for indicator in analysis.indicators
        )
    else:
        event_description = "intelligence event"

    if analysis.entities:
        entity_names = ", ".join(
            entity.display_name
            for entity in analysis.entities
        )

        return (
            f"{group.event_count} {report_word} from "
            f"{group.source_count} {source_word} describe "
            f"{event_description} involving {entity_names}."
        )

    return (
        f"{group.event_count} {report_word} from "
        f"{group.source_count} {source_word} describe "
        f"{event_description}."
    )


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

    summary = _build_fused_summary(
        group,
        analysis,
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
        summary=summary,
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