"""Integration tests for live pipeline incident resolution."""

from pathlib import Path
from types import SimpleNamespace

import pytest

import app.intelligence.pipeline as pipeline_module
from app.enums.source import (
    SourceAuthority,
    SourceReliability,
)
from app.intelligence.pipeline import collect_intelligence_run
from app.models.normalized_event import NormalizedEvent
from app.storage.database import EventRepository
from app.storage.incident_repository import IncidentRepository


def make_event(
    event_uid: str,
    title: str,
    *,
    source_name: str,
) -> NormalizedEvent:
    """Create deterministic normalized evidence for pipeline tests."""
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


def install_feed(
    monkeypatch: pytest.MonkeyPatch,
    event: NormalizedEvent,
) -> None:
    """Install one deterministic fake RSS source and report."""
    source = SimpleNamespace(
        display_name=event.source_name
    )

    def fake_sources(
        *,
        collector: str,
    ) -> tuple[SimpleNamespace, ...]:
        assert collector == "rss"

        return (
            source,
        )

    def fake_collect_feed(
        selected_source: SimpleNamespace,
    ) -> list[NormalizedEvent]:
        assert selected_source is source

        return [
            event,
        ]

    monkeypatch.setattr(
        pipeline_module,
        "get_enabled_sources",
        fake_sources,
    )

    monkeypatch.setattr(
        pipeline_module,
        "collect_feed",
        fake_collect_feed,
    )


def initialize_repositories(
    database_path: Path,
) -> tuple[
    EventRepository,
    IncidentRepository,
]:
    """Return initialized repositories sharing one database."""
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


def test_pipeline_remains_compatible_without_incident_repository(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Collection still works when incident persistence is disabled."""
    database_path = (
        tmp_path
        / "clim.db"
    )

    event_repository = EventRepository(
        database_path
    )

    event_repository.initialize()

    event = make_event(
        "event-1",
        "China launches military exercises around Taiwan",
        source_name="Reuters",
    )

    install_feed(
        monkeypatch,
        event,
    )

    result = collect_intelligence_run(
        event_repository
    )

    assert result.discovered == 1
    assert result.inserted == 1

    assert result.new_events == (
        event,
    )

    assert result.incident_updates == ()

    assert event_repository.count() == 1


def test_pipeline_persists_incident_for_new_report(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A newly stored report is assigned to a persistent incident."""
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

    event = make_event(
        "event-1",
        "China launches military exercises around Taiwan",
        source_name="Reuters",
    )

    install_feed(
        monkeypatch,
        event,
    )

    result = collect_intelligence_run(
        event_repository,
        incident_repository,
    )

    assert result.inserted == 1

    assert len(
        result.incident_updates
    ) == 1

    update = result.incident_updates[0]

    assert update.matched_existing is False

    assert update.incident.event_uids == (
        "event-1",
    )

    assert incident_repository.count() == 1

    stored = incident_repository.find_by_event(
        "event-1"
    )

    assert stored is not None

    assert (
        stored.incident_uid
        == update.incident.incident_uid
    )


def test_duplicate_report_does_not_create_incident_update(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Duplicate evidence does not touch incident membership."""
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

    event = make_event(
        "event-1",
        "China launches military exercises around Taiwan",
        source_name="Reuters",
    )

    install_feed(
        monkeypatch,
        event,
    )

    first = collect_intelligence_run(
        event_repository,
        incident_repository,
    )

    second = collect_intelligence_run(
        event_repository,
        incident_repository,
    )

    assert first.inserted == 1

    assert len(
        first.incident_updates
    ) == 1

    assert second.discovered == 1
    assert second.inserted == 0
    assert second.new_events == ()
    assert second.incident_updates == ()

    assert event_repository.count() == 1
    assert incident_repository.count() == 1

    incident = incident_repository.find_by_event(
        "event-1"
    )

    assert incident is not None
    assert incident.event_count == 1


def test_pipeline_joins_related_report_after_restart(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Separate collection runs converge on one persistent incident."""
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

    reuters = make_event(
        "reuters-1",
        "China launches military exercises around Taiwan",
        source_name="Reuters",
    )

    install_feed(
        monkeypatch,
        reuters,
    )

    first_run = collect_intelligence_run(
        first_event_repository,
        first_incident_repository,
    )

    assert len(
        first_run.incident_updates
    ) == 1

    original_incident_uid = (
        first_run
        .incident_updates[0]
        .incident
        .incident_uid
    )

    (
        second_event_repository,
        second_incident_repository,
    ) = initialize_repositories(
        database_path
    )

    bbc = make_event(
        "bbc-1",
        "China begins military exercises around Taiwan",
        source_name="BBC",
    )

    install_feed(
        monkeypatch,
        bbc,
    )

    second_run = collect_intelligence_run(
        second_event_repository,
        second_incident_repository,
    )

    assert second_run.inserted == 1

    assert len(
        second_run.incident_updates
    ) == 1

    update = second_run.incident_updates[0]

    assert update.matched_existing is True

    assert (
        update.incident.incident_uid
        == original_incident_uid
    )

    assert update.incident.event_uids == (
        "reuters-1",
        "bbc-1",
    )

    assert update.correlation_score >= 0.40

    assert second_incident_repository.count() == 1