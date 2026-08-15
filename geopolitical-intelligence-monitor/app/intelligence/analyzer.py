"""Integrated intelligence analysis for CLIM."""

from __future__ import annotations

from dataclasses import dataclass

from app.enums.escalation import Escalation
from app.enums.impact import Impact
from app.enums.source import SourceAuthority, SourceReliability
from app.intelligence.confidence import ConfidenceResult, assess_confidence
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
    reasoning: tuple[str, ...]
    confidence: ConfidenceResult


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
    """Combine escalation effects into a bounded result."""
    if not indicators:
        return Escalation.NEUTRAL

    raw_score = sum(
        int(indicator.escalation)
        for indicator in indicators
    )

    bounded_score = max(
        int(Escalation.DECREASE_MAJOR),
        min(
            int(Escalation.INCREASE_MAJOR),
            raw_score,
        ),
    )

    return Escalation(bounded_score)


def _build_reasoning(
    entities: tuple[IntelligenceEntity, ...],
    indicators: tuple[IntelligenceIndicator, ...],
    theaters: tuple[IntelligenceTheater, ...],
    impact: Impact,
    escalation: Escalation,
) -> tuple[str, ...]:
    """Build a human-readable explanation of the analysis."""
    reasons: list[str] = []

    for entity in entities:
        reasons.append(
            f"Detected entity: {entity.display_name}"
        )

    for indicator in indicators:
        reasons.append(
            f"Detected indicator: {indicator.display_name} "
            f"(impact={indicator.impact.name}, "
            f"escalation={indicator.escalation.name})"
        )

    for theater in theaters:
        reasons.append(
            f"Assigned theater: {theater.display_name}"
        )

    reasons.append(
        f"Overall impact: {impact.name}"
    )

    reasons.append(
        f"Overall escalation: {escalation.name}"
    )

    return tuple(reasons)


def analyze(
    text: str,
    *,
    authority: SourceAuthority = SourceAuthority.UNKNOWN,
    reliability: SourceReliability = SourceReliability.UNKNOWN,
    corroborating_sources: int = 1,
) -> AnalysisResult:
    """
    Analyze supplied text using CLIM ontology and intelligence rules.

    Source provenance may be supplied when known. Defaults represent an
    unverified single-source event.
    """
    entities = find_entities(text)
    indicators = find_indicators(text)
    theaters = _resolve_theaters(entities)

    impact = _highest_impact(indicators)
    escalation = _combined_escalation(indicators)

    reasoning = _build_reasoning(
        entities=entities,
        indicators=indicators,
        theaters=theaters,
        impact=impact,
        escalation=escalation,
    )

    confidence = assess_confidence(
        authority=authority,
        reliability=reliability,
        corroborating_sources=corroborating_sources,
    )

    return AnalysisResult(
        text=text,
        entities=entities,
        indicators=indicators,
        theaters=theaters,
        impact=impact,
        escalation=escalation,
        reasoning=reasoning,
        confidence=confidence,
    )