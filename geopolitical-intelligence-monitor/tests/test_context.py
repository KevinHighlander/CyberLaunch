"""Tests for the CLIM context engine."""

from app.intelligence.context import build_context
from app.ontology.entities import get_entity


def test_russia_china_context() -> None:
    russia = get_entity("russia")
    china = get_entity("china")

    assert russia is not None
    assert china is not None

    result = build_context(
        (
            russia,
            china,
        )
    )

    assert (
        "Russia and China have a known "
        "strategic partnership relationship."
        in result.statements
    )


def test_russia_north_korea_context() -> None:
    russia = get_entity("russia")
    north_korea = get_entity("north-korea")

    assert russia is not None
    assert north_korea is not None

    result = build_context(
        (
            russia,
            north_korea,
        )
    )

    assert (
        "Russia and North Korea have a known "
        "military cooperation relationship."
        in result.statements
    )


def test_unrelated_entities_have_no_context() -> None:
    iran = get_entity("iran")
    japan = get_entity("japan")

    assert iran is not None
    assert japan is not None

    result = build_context(
        (
            iran,
            japan,
        )
    )

    assert result.statements == ()


def test_context_does_not_duplicate_relationships() -> None:
    russia = get_entity("russia")
    china = get_entity("china")

    assert russia is not None
    assert china is not None

    result = build_context(
        (
            russia,
            china,
        )
    )

    assert len(result.statements) == 1