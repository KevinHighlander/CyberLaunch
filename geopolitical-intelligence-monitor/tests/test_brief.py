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