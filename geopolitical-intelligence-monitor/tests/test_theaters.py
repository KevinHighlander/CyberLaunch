"""Tests for CLIM geopolitical theaters."""

from app.ontology.theaters import (
    get_all_theaters,
    get_theater,
    get_theaters_for_domain,
)


def test_russia_is_first_class_theater() -> None:
    theater = get_theater("russia")

    assert theater is not None
    assert theater.display_name == "Russia"
    assert theater.domain_key == "geopolitics"


def test_indo_pacific_theater_exists() -> None:
    theater = get_theater("indo-pacific")

    assert theater is not None
    assert theater.display_name == "Indo-Pacific"


def test_geopolitical_domain_contains_theaters() -> None:
    theaters = get_theaters_for_domain("geopolitics")

    assert len(theaters) >= 7
    assert any(theater.key == "russia" for theater in theaters)


def test_unknown_domain_returns_no_theaters() -> None:
    assert get_theaters_for_domain("not-real") == ()


def test_all_theaters_are_registered() -> None:
    assert len(get_all_theaters()) >= 7