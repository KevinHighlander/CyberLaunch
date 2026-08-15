"""Tests for CLIM intelligence indicators."""

from app.enums.escalation import Escalation
from app.enums.impact import Impact
from app.intelligence.indicators import (
    find_indicators,
    get_indicator,
    get_indicators_by_category,
)


def test_ballistic_missile_indicator_exists() -> None:
    indicator = get_indicator("ballistic-missile-launch")

    assert indicator is not None
    assert indicator.impact is Impact.CRITICAL
    assert indicator.escalation is Escalation.INCREASE_MAJOR


def test_ballistic_missile_launch_is_detected() -> None:
    matches = find_indicators(
        "North Korea conducted a ballistic missile launch early Tuesday."
    )

    assert any(
        indicator.key == "ballistic-missile-launch"
        for indicator in matches
    )


def test_military_exercise_is_detected() -> None:
    matches = find_indicators(
        "China announced new military exercises around Taiwan."
    )

    assert any(
        indicator.key == "military-exercise"
        for indicator in matches
    )


def test_ceasefire_reduces_escalation() -> None:
    indicator = get_indicator("ceasefire")

    assert indicator is not None
    assert indicator.impact is Impact.CRITICAL
    assert indicator.escalation is Escalation.DECREASE_MAJOR


def test_critical_infrastructure_attack_is_detected() -> None:
    matches = find_indicators(
        "Officials reported a critical infrastructure cyberattack."
    )

    assert any(
        indicator.key == "critical-infrastructure-cyberattack"
        for indicator in matches
    )


def test_military_category_returns_indicators() -> None:
    indicators = get_indicators_by_category("military")

    assert len(indicators) >= 5
    assert all(
        indicator.category == "military"
        for indicator in indicators
    )


def test_unknown_indicator_returns_none() -> None:
    assert get_indicator("space-laser-death-ray") is None


def test_irrelevant_text_has_no_indicators() -> None:
    matches = find_indicators(
        "A teenager has announced plans to debut in a K-pop group."
    )

    assert matches == ()