"""CLIM collection and analysis orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from app.collectors.rss import (
    FeedCollectionError,
    collect_feed,
)
from app.intelligence.analyzer import AnalysisResult, analyze
from app.intelligence.incident_service import (
    IncidentUpdate,
    resolve_and_persist_incident,
)
from app.models.analyzed_event import AnalyzedEvent
from app.models.normalized_event import NormalizedEvent
from app.sources import get_enabled_sources
from app.storage.database import EventRepository
from app.storage.incident_repository import IncidentRepository


@dataclass(frozen=True, slots=True)
class ProcessedEvent:
    """A normalized report and both forms of its analysis."""

    normalized: NormalizedEvent
    analysis: AnalysisResult
    analyzed: AnalyzedEvent


@dataclass(frozen=True, slots=True)
class CollectionNotice:
    """A structured message produced during collection."""

    level: str
    source_name: str
    message: str


@dataclass(frozen=True, slots=True)
class CollectionRun:
    """Results from one CLIM collection cycle."""

    discovered: int
    inserted: int
    new_events: tuple[NormalizedEvent, ...]
    analyses: tuple[AnalysisResult, ...]
    notices: tuple[CollectionNotice, ...]
    incident_updates: tuple[IncidentUpdate, ...]


def process_event(
    event: NormalizedEvent,
) -> ProcessedEvent:
    """Analyze one normalized event and prepare it for persistence."""
    analysis = analyze(
        event.analysis_text,
        authority=event.source_authority,
        reliability=event.source_reliability,
        corroborating_sources=1,
    )

    if analysis.theaters:
        region = analysis.theaters[0].display_name
    elif event.region_hint:
        region = event.region_hint
    else:
        region = "unclassified"

    if analysis.indicators:
        highest_indicator = max(
            analysis.indicators,
            key=lambda indicator: int(
                indicator.impact
            ),
        )
        category = highest_indicator.category
    else:
        category = "general"

    analyzed = AnalyzedEvent(
        event_uid=event.event_uid,
        title=event.title,
        summary=event.summary,
        source_name=event.source_name,
        source_url=event.source_url,
        source_type=event.source_type,
        source_country=event.source_country,
        source_authority=event.source_authority,
        source_reliability=event.source_reliability,
        published_at=event.published_at,
        collected_at=datetime.now(
            timezone.utc
        ),
        region=region,
        category=category,
        significance=int(
            analysis.impact
        ),
        confidence=analysis.confidence.level,
    )

    return ProcessedEvent(
        normalized=event,
        analysis=analysis,
        analyzed=analyzed,
    )


def analyze_event(
    event: NormalizedEvent,
) -> AnalyzedEvent:
    """Convert a normalized report into a persistable analyzed event."""
    return process_event(
        event
    ).analyzed


def collect_intelligence_run(
    repository: EventRepository,
    incident_repository: IncidentRepository | None = None,
) -> CollectionRun:
    """Collect, analyze, store, and retain fresh intelligence analysis."""
    discovered = 0
    inserted = 0

    new_events: list[NormalizedEvent] = []
    analyses: list[AnalysisResult] = []
    notices: list[CollectionNotice] = []
    incident_updates: list[IncidentUpdate] = []

    for source in get_enabled_sources(
        collector="rss"
    ):
        notices.append(
            CollectionNotice(
                level="collect",
                source_name=source.display_name,
                message=(
                    f"Collecting "
                    f"{source.display_name}"
                ),
            )
        )

        try:
            events = collect_feed(
                source
            )

        except FeedCollectionError as error:
            notices.append(
                CollectionNotice(
                    level="error",
                    source_name=source.display_name,
                    message=str(
                        error
                    ),
                )
            )
            continue

        discovered += len(
            events
        )

        for normalized_event in events:
            processed = process_event(
                normalized_event
            )

            if not repository.insert(
                processed.analyzed
            ):
                continue

            inserted += 1

            new_events.append(
                processed.normalized
            )

            analyses.append(
                processed.analysis
            )

            if incident_repository is None:
                continue

            incident_update = (
                resolve_and_persist_incident(
                    processed.normalized,
                    event_repository=repository,
                    incident_repository=incident_repository,
                    observed_at=processed.analyzed.collected_at,
                )
            )

            incident_updates.append(
                incident_update
            )

    return CollectionRun(
        discovered=discovered,
        inserted=inserted,
        new_events=tuple(
            new_events
        ),
        analyses=tuple(
            analyses
        ),
        notices=tuple(
            notices
        ),
        incident_updates=tuple(
            incident_updates
        ),
    )


def collect_intelligence(
    repository: EventRepository,
    incident_repository: IncidentRepository | None = None,
) -> tuple[int, int]:
    """Collect, analyze, and store enabled RSS sources."""
    result = collect_intelligence_run(
        repository,
        incident_repository,
    )

    return (
        result.discovered,
        result.inserted,
    )