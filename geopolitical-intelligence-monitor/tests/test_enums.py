"""Tests for CLIM enums."""

from app.enums.impact import Impact
from app.enums.escalation import Escalation


def test_impact_order() -> None:
    assert Impact.CRITICAL > Impact.HIGH
    assert Impact.HIGH > Impact.MODERATE


def test_escalation_values() -> None:
    assert Escalation.INCREASE_MAJOR > Escalation.INCREASE
    assert Escalation.NEUTRAL == 0
    assert Escalation.DECREASE_MAJOR < 0