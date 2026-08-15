"""Tests for CLIM significance scoring."""

from app.intelligence.significance import score_event


def test_irrelevant_entertainment_is_routine() -> None:
    result = score_event("Baby Shark Boy set to make K-pop debut")
    assert result.score == 0
    assert result.level == "routine"


def test_north_korea_ballistic_missile_is_high_priority() -> None:
    result = score_event("North Korea conducts ballistic missile launch")
    assert result.score >= 9
    assert result.category == "military"


def test_critical_infrastructure_cyberattack_is_significant() -> None:
    result = score_event(
        "Taiwan hit by major cyberattack against critical infrastructure"
    )
    assert result.score >= 6
    assert result.category == "cyber"
