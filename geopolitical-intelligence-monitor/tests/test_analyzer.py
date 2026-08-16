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


def test_analysis_includes_reasoning() -> None:
    result = analyze(
        "North Korea conducted a ballistic missile launch."
    )

    assert any(
        reason == "Detected entity: North Korea"
        for reason in result.reasoning
    )

    assert any(
        reason.startswith(
            "Detected indicator: Ballistic Missile Launch"
        )
        for reason in result.reasoning
    )

    assert "Assigned theater: Indo-Pacific" in result.reasoning
    assert "Overall impact: CRITICAL" in result.reasoning
    assert "Overall escalation: INCREASE_MAJOR" in result.reasoning


def test_irrelevant_analysis_still_explains_result() -> None:
    result = analyze(
        "A teenager announced plans to debut in a K-pop group."
    )

    assert result.reasoning == (
        "Overall impact: MINIMAL",
        "Overall escalation: NEUTRAL",
    )


def test_analysis_contains_confidence() -> None:
    result = analyze(
        "North Korea conducted a ballistic missile launch."
    )

    assert result.confidence.score >= 0
    assert result.confidence.level is not None


def test_confidence_contains_reasoning() -> None:
    result = analyze(
        "China announced military exercises around Taiwan."
    )

    assert len(result.confidence.reasons) > 0


def test_analysis_reports_known_relationship() -> None:
    result = analyze(
        "Russia and China announced new military exercises."
    )

    assert (
        "Known relationship: "
        "Russia ↔ China — strategic-partnership"
        in result.reasoning
    )


def test_analysis_reports_russia_north_korea_relationship() -> None:
    result = analyze(
        "Russia and North Korea announced expanded military cooperation."
    )

    assert (
        "Known relationship: "
        "Russia ↔ North Korea — military-cooperation"
        in result.reasoning
    )


def test_unrelated_entities_do_not_create_fake_relationship() -> None:
    result = analyze(
        "Iran and Japan issued separate statements."
    )

    assert not any(
        reason.startswith(
            "Known relationship:"
        )
        for reason in result.reasoning
    )


def test_relationship_is_reported_only_once() -> None:
    result = analyze(
        "China and Russia announced joint military exercises."
    )

    relationship_reasons = [
        reason
        for reason in result.reasoning
        if reason.startswith(
            "Known relationship:"
        )
    ]

    assert len(relationship_reasons) == 1