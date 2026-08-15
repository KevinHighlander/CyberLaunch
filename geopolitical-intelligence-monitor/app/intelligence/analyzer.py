"""Integrated intelligence analysis for CLIM."""

from __future__ import annotations

from dataclasses import dataclass

from app.enums.escalation import Escalation
from app.enums.impact import Impact
from app.intelligence.indicators import IntelligenceIndicator, find_indicators
from app.ontology.entities import IntelligenceEntity, find_entities
from app.ontology.theaters import IntelligenceTheater, get_theater


@dataclass(frozen=True, slots=True)
class AnalysisResult:
    """Structured analysis generated from supplied text."""

    text: str
    entities: tuple[IntelligenceEntity, ...]
    indicators: tuple[IntelligenceIndicator, ...]
    theaters: tuple[IntelligenceTheater, ...]
    impact: Impact
    escalation: Escalation


def _resolve_theaters(
    entities: tuple[IntelligenceEntity, ...],
) -> tuple[IntelligenceTheater, ...]:
    """Resolve unique theaters associated with detected entities."""
    theater_keys: set[str] = set()

    for entity in entities:
        theater_keys.update(entity.theater_keys)

    theaters: list[IntelligenceTheater] = []

    for key in sorted(theater_keys):
        theater = get_theater(key)

        if theater is not None:
            theaters.append(theater)

    return tuple(theaters)


def _highest_impact(
    indicators: tuple[IntelligenceIndicator, ...],
) -> Impact:
    """Return the highest impact among detected indicators."""
    if not indicators:
        return Impact.MINIMAL

    return max(indicator.impact for indicator in indicators)


def _combined_escalation(
    indicators: tuple[IntelligenceIndicator, ...],
) -> Escalation:
    """
    Combine indicator escalation effects into a bounded result.

    Multiple indicators may reinforce one another, but the final result is
    constrained to the supported Escalation range.
    """
    if not indicators:
        return Escalation.NEUTRAL

    raw_score = sum(int(indicator.escalation) for indicator in indicators)

    bounded_score = max(
        int(Escalation.DECREASE_MAJOR),
        min(int(Escalation.INCREASE_MAJOR), raw_score),
    )

    return Escalation(bounded_score)


def analyze(text: str) -> AnalysisResult:
    """Analyze supplied text using CLIM ontology and indicators."""
    entities = find_entities(text)
    indicators = find_indicators(text)
    theaters = _resolve_theaters(entities)

    return AnalysisResult(
        text=text,
        entities=entities,
        indicators=indicators,
        theaters=theaters,
        impact=_highest_impact(indicators),
        escalation=_combined_escalation(indicators),
    )