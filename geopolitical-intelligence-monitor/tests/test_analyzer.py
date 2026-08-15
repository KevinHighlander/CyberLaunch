"""Integration tests for the CLIM intelligence analyzer."""

from app.enums.escalation import Escalation
from app.enums.impact import Impact
from app.intelligence.analyzer import analyze


def test_north_korea_ballistic_missile_analysis() -> None:
    result = analyze(
        "North Korea conducted a ballistic missile launch early Tuesday."
    )

    assert any(
        entity.key == "north-korea"
        for entity in result.entities
    )

    assert any(
        indicator.key == "ballistic-missile-launch"
        for indicator in result.indicators
    )

    assert any(
        theater.key == "indo-pacific"
        for theater in result.theaters
    )

    assert result.impact is Impact.CRITICAL
    assert result.escalation is Escalation.INCREASE_MAJOR


def test_taiwan_military_exercise_analysis() -> None:
    result = analyze(
        "China announced new military exercises around Taiwan."
    )

    entity_keys = {
        entity.key
        for entity in result.entities
    }

    assert "china" in entity_keys
    assert "taiwan" in entity_keys

    assert any(
        indicator.key == "military-exercise"
        for indicator in result.indicators
    )

    assert result.impact is Impact.MODERATE
    assert result.escalation is Escalation.INCREASE_MINOR


def test_ceasefire_reduces_escalation() -> None:
    result = analyze(
        "Iran announced a ceasefire after diplomatic negotiations."
    )

    assert any(
        entity.key == "iran"
        for entity in result.entities
    )

    assert any(
        indicator.key == "ceasefire"
        for indicator in result.indicators
    )

    assert result.impact is Impact.CRITICAL
    assert result.escalation is Escalation.DECREASE_MAJOR


def test_multiple_indicators_combine_escalation() -> None:
    result = analyze(
        "North Korea announced military exercises and a ballistic missile launch."
    )

    assert result.impact is Impact.CRITICAL
    assert result.escalation is Escalation.INCREASE_MAJOR


def test_irrelevant_text_returns_minimal_analysis() -> None:
    result = analyze(
        "A teenager announced plans to debut in a K-pop group."
    )

    assert result.entities == ()
    assert result.indicators == ()
    assert result.theaters == ()
    assert result.impact is Impact.MINIMAL
    assert result.escalation is Escalation.NEUTRAL