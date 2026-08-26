"""Integration tests for persistent CLIM incident orchestration."""

from datetime import datetime, timedelta, timezone
from pathlib import Path

from app.enums.confidence import Confidence
from app.enums.source import (
    SourceAuthority,
    SourceReliability,
)
from app.intelligence.incident_service import (
    resolve_and_persist_incident,
)
from app.models.analyzed_event import AnalyzedEvent
from app.models.normalized_event import NormalizedEvent
from app.storage.database import EventRepository
from app.storage.incident_repository import IncidentRepository


_BASE_TIME = datetime(
    2026,
    8,
    26,
    12,
    0,
    tzinfo=timezone.utc,
)


def make_normalized_event(
    event_uid: str,
    title: str,
    *,
    source_name: str,
) -> NormalizedEvent:
    """Create deterministic normalized evidence."""
    return NormalizedEvent(
        event_uid=event_uid,
        title=title,
        summary="",
        source_name=source_name,
        source_url=(
            f"https://example.com/{event_uid}"
        ),
        source_type="media",
        source_country="United States",
        source_authority=(
            SourceAuthority.SECONDARY
        ),
        source_reliability=(
            SourceReliability.HIGH
        ),
        published_at=None,
        region_hint=None,
    )


def make_analyzed_event(
    event: NormalizedEvent,
    *,
    collected_at: datetime,
) -> AnalyzedEvent:
    """Create persistable evidence from a normalized report."""
    return AnalyzedEvent(
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
        collected_at=collected_at,
        region="Indo-Pacific",
        category="military",
        significance=3,
        confidence=Confidence.MEDIUM,
    )


def initialize_repositories(
    database_path: Path,
) -> tuple[
    EventRepository,
    IncidentRepository,
]:
    """Return initialized repositories sharing one SQLite database."""
    event_repository = EventRepository(
        database_path
    )

    incident_repository = IncidentRepository(
        database_path
    )

    event_repository.initialize()
    incident_repository.initialize()

    return (
        event_repository,
        incident_repository,
    )


def test_first_report_creates_persistent_incident(
    tmp_path: Path,
) -> None:
    database_path = (
        tmp_path
        / "clim.db"
    )

    (
        event_repository,
        incident_repository,
    ) = initialize_repositories(
        database_path
    )

    reuters = make_normalized_event(
        "reuters-1",
        "China launches military exercises around Taiwan",
        source_name="Reuters",
    )

    event_repository.insert(
        make_analyzed_event(
            reuters,
            collected_at=_BASE_TIME,
        )
    )

    update = resolve_and_persist_incident(
        reuters,
        event_repository=event_repository,
        incident_repository=incident_repository,
        observed_at=_BASE_TIME,
    )

    assert update.matched_existing is False
    assert update.correlation_score == 0.0

    assert update.incident.event_uids == (
        "reuters-1",
    )

    assert incident_repository.count() == 1

    loaded = incident_repository.get(
        update.incident.incident_uid
    )

    assert loaded is not None

    assert loaded.event_uids == (
        "reuters-1",
    )


def test_related_report_joins_incident_after_repository_restart(
    tmp_path: Path,
) -> None:
    database_path = (
        tmp_path
        / "clim.db"
    )

    (
        first_event_repository,
        first_incident_repository,
    ) = initialize_repositories(
        database_path
    )

    reuters = make_normalized_event(
        "reuters-1",
        "China launches military exercises around Taiwan",
        source_name="Reuters",
    )

    first_event_repository.insert(
        make_analyzed_event(
            reuters,
            collected_at=_BASE_TIME,
        )
    )

    first_update = resolve_and_persist_incident(
        reuters,
        event_repository=first_event_repository,
        incident_repository=first_incident_repository,
        observed_at=_BASE_TIME,
    )

    original_incident_uid = (
        first_update.incident.incident_uid
    )

    (
        second_event_repository,
        second_incident_repository,
    ) = initialize_repositories(
        database_path
    )

    bbc = make_normalized_event(
        "bbc-1",
        "China begins military exercises around Taiwan",
        source_name="BBC",
    )

    second_event_repository.insert(
        make_analyzed_event(
            bbc,
            collected_at=(
                _BASE_TIME
                + timedelta(
                    hours=1
                )
            ),
        )
    )

    second_update = resolve_and_persist_incident(
        bbc,
        event_repository=second_event_repository,
        incident_repository=second_incident_repository,
        observed_at=(
            _BASE_TIME
            + timedelta(
                hours=1
            )
        ),
    )

    assert second_update.matched_existing is True

    assert (
        second_update.incident.incident_uid
        == original_incident_uid
    )

    assert second_update.incident.event_uids == (
        "reuters-1",
        "bbc-1",
    )

    assert second_update.correlation_score >= 0.40

    assert second_incident_repository.count() == 1


def test_unrelated_report_creates_second_incident(
    tmp_path: Path,
) -> None:
    database_path = (
        tmp_path
        / "clim.db"
    )

    (
        event_repository,
        incident_repository,
    ) = initialize_repositories(
        database_path
    )

    reuters = make_normalized_event(
        "reuters-1",
        "China launches military exercises around Taiwan",
        source_name="Reuters",
    )

    event_repository.insert(
        make_analyzed_event(
            reuters,
            collected_at=_BASE_TIME,
        )
    )

    first_update = resolve_and_persist_incident(
        reuters,
        event_repository=event_repository,
        incident_repository=incident_repository,
        observed_at=_BASE_TIME,
    )

    missile_report = make_normalized_event(
        "missile-1",
        "North Korea conducts ballistic missile launch",
        source_name="BBC",
    )

    event_repository.insert(
        make_analyzed_event(
            missile_report,
            collected_at=(
                _BASE_TIME
                + timedelta(
                    hours=1
                )
            ),
        )
    )

    second_update = resolve_and_persist_incident(
        missile_report,
        event_repository=event_repository,
        incident_repository=incident_repository,
        observed_at=(
            _BASE_TIME
            + timedelta(
                hours=1
            )
        ),
    )

    assert second_update.matched_existing is False

    assert (
        second_update.incident.incident_uid
        != first_update.incident.incident_uid
    )

    assert incident_repository.count() == 2


def test_persisted_historical_evidence_drives_resolution(
    tmp_path: Path,
) -> None:
    database_path = (
        tmp_path
        / "clim.db"
    )

    (
        event_repository,
        incident_repository,
    ) = initialize_repositories(
        database_path
    )

    historical = make_normalized_event(
        "historical-1",
        "China launches military exercises around Taiwan",
        source_name="Reuters",
    )

    event_repository.insert(
        make_analyzed_event(
            historical,
            collected_at=_BASE_TIME,
        )
    )

    original_update = resolve_and_persist_incident(
        historical,
        event_repository=event_repository,
        incident_repository=incident_repository,
        observed_at=_BASE_TIME,
    )

    fresh = make_normalized_event(
        "fresh-1",
        "China begins military exercises around Taiwan",
        source_name="BBC",
    )

    fresh_update = resolve_and_persist_incident(
        fresh,
        event_repository=event_repository,
        incident_repository=incident_repository,
        observed_at=(
            _BASE_TIME
            + timedelta(
                minutes=30
            )
        ),
    )

    assert fresh_update.matched_existing is True

    assert (
        fresh_update.incident.incident_uid
        == original_update.incident.incident_uid
    )

    assert fresh_update.incident.event_uids == (
        "historical-1",
        "fresh-1",
    )


def test_custom_threshold_can_force_new_incident(
    tmp_path: Path,
) -> None:
    database_path = (
        tmp_path
        / "clim.db"
    )

    (
        event_repository,
        incident_repository,
    ) = initialize_repositories(
        database_path
    )

    first = make_normalized_event(
        "event-1",
        "China launches military exercises around Taiwan",
        source_name="Reuters",
    )

    event_repository.insert(
        make_analyzed_event(
            first,
            collected_at=_BASE_TIME,
        )
    )

    first_update = resolve_and_persist_incident(
        first,
        event_repository=event_repository,
        incident_repository=incident_repository,
        observed_at=_BASE_TIME,
    )

    second = make_normalized_event(
        "event-2",
        "China begins military exercises around Taiwan",
        source_name="BBC",
    )

    second_update = resolve_and_persist_incident(
        second,
        event_repository=event_repository,
        incident_repository=incident_repository,
        observed_at=(
            _BASE_TIME
            + timedelta(
                hours=1
            )
        ),
        threshold=0.90,
    )

    assert second_update.matched_existing is False

    assert (
        second_update.incident.incident_uid
        != first_update.incident.incident_uid
    )

    assert incident_repository.count() == 2