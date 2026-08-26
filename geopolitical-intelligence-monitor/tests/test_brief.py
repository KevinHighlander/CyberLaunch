"""Tests for deterministic intelligence briefing."""

from app.intelligence.analyzer import analyze
from app.reporting.brief import build_brief


def test_brief_contains_header() -> None:
    brief = build_brief(
        analyze(
            "Russia and China announced military exercises."
        )
    )

    assert "CYBERLAUNCH INTELLIGENCE BRIEF" in brief


def test_brief_contains_confidence() -> None:
    brief = build_brief(
        analyze(
            "Russia and China announced military exercises."
        )
    )

    assert "Confidence" in brief


def test_brief_contains_relationship_context() -> None:
    brief = build_brief(
        analyze(
            "Russia and China announced military exercises."
        )
    )

    assert "Strategic Context" in brief
    assert "strategic-partnership" in brief


def test_brief_is_deterministic() -> None:
    analysis = analyze(
        "Russia and China announced military exercises."
    )

    assert (
        build_brief(analysis)
        == build_brief(analysis)
    )

def test_fused_brief_contains_corroboration() -> None:
    from app.enums.source import (
        SourceAuthority,
        SourceReliability,
    )
    from app.intelligence.fusion import fuse_events
    from app.models.normalized_event import NormalizedEvent
    from app.reporting.brief import build_fused_brief

    events = [
        NormalizedEvent(
            event_uid="reuters-taiwan",
            title=(
                "China launches military exercises "
                "around Taiwan"
            ),
            summary="",
            source_name="Reuters",
            source_url="https://example.com/reuters",
            source_type="media",
            source_country="United Kingdom",
            source_authority=SourceAuthority.SECONDARY,
            source_reliability=SourceReliability.HIGH,
        ),
        NormalizedEvent(
            event_uid="bbc-taiwan",
            title=(
                "China begins military drills "
                "near Taiwan"
            ),
            summary="",
            source_name="BBC",
            source_url="https://example.com/bbc",
            source_type="media",
            source_country="United Kingdom",
            source_authority=SourceAuthority.SECONDARY,
            source_reliability=SourceReliability.HIGH,
        ),
    ]

    brief = build_fused_brief(
        fuse_events(events)[0]
    )

    assert "CYBERLAUNCH FUSED INTELLIGENCE BRIEF" in brief
    assert "Independent Sources: 2" in brief
    assert "Corroborated: YES" in brief


def test_fused_brief_contains_source_diversity() -> None:
    from app.enums.source import (
        SourceAuthority,
        SourceReliability,
    )
    from app.intelligence.fusion import fuse_events
    from app.models.normalized_event import NormalizedEvent
    from app.reporting.brief import build_fused_brief

    event = NormalizedEvent(
        event_uid="reuters-taiwan",
        title=(
            "China launches military exercises "
            "around Taiwan"
        ),
        summary="",
        source_name="Reuters",
        source_url="https://example.com/reuters",
        source_type="media",
        source_country="United Kingdom",
        source_authority=SourceAuthority.SECONDARY,
        source_reliability=SourceReliability.HIGH,
    )

    brief = build_fused_brief(
        fuse_events([event])[0]
    )

    assert "Source Diversity" in brief
    assert "Score:" in brief


def test_fused_brief_labels_graph_context_as_background() -> None:
    from app.enums.source import (
        SourceAuthority,
        SourceReliability,
    )
    from app.intelligence.fusion import fuse_events
    from app.models.normalized_event import NormalizedEvent
    from app.reporting.brief import build_fused_brief

    event = NormalizedEvent(
        event_uid="china-taiwan",
        title=(
            "China launches military exercises "
            "around Taiwan"
        ),
        summary="",
        source_name="Reuters",
        source_url="https://example.com/reuters",
        source_type="media",
        source_country="United Kingdom",
        source_authority=SourceAuthority.SECONDARY,
        source_reliability=SourceReliability.HIGH,
    )

    brief = build_fused_brief(
        fuse_events([event])[0]
    )

    assert "Knowledge Context" in brief
    assert (
        "not evidence of event involvement"
        in brief
    )