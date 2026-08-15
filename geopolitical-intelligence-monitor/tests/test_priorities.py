"""Tests for CLIM operational theater priorities."""

from app.watchlists.priorities import get_theater_priority


def test_russia_is_high_priority() -> None:
    assert get_theater_priority("russia") == 5


def test_indo_pacific_is_high_priority() -> None:
    assert get_theater_priority("indo-pacific") == 5


def test_unknown_theater_has_zero_priority() -> None:
    assert get_theater_priority("not-real") == 0