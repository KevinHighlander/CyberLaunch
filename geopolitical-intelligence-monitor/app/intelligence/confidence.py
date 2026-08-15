"""Confidence assessment for CLIM intelligence events."""

from __future__ import annotations

from dataclasses import dataclass

from app.enums.confidence import Confidence
from app.enums.source import SourceAuthority, SourceReliability


@dataclass(frozen=True, slots=True)
class ConfidenceResult:
    """Explainable confidence assessment."""

    level: Confidence
    score: int
    reasons: tuple[str, ...]


AUTHORITY_SCORES: dict[SourceAuthority, int] = {
    SourceAuthority.PRIMARY: 30,
    SourceAuthority.SECONDARY: 20,
    SourceAuthority.UNKNOWN: 5,
}


RELIABILITY_SCORES: dict[SourceReliability, int] = {
    SourceReliability.OFFICIAL: 30,
    SourceReliability.HIGH: 25,
    SourceReliability.MEDIUM: 15,
    SourceReliability.LOW: 5,
    SourceReliability.UNKNOWN: 0,
}


def _corroboration_score(source_count: int) -> int:
    """Return confidence contribution from independent corroboration."""
    if source_count >= 4:
        return 40
    if source_count == 3:
        return 30
    if source_count == 2:
        return 20
    if source_count == 1:
        return 5
    return 0


def _level_for_score(score: int) -> Confidence:
    """Map a numeric score to a confidence level."""
    if score >= 85:
        return Confidence.VERY_HIGH
    if score >= 65:
        return Confidence.HIGH
    if score >= 40:
        return Confidence.MEDIUM
    if score >= 20:
        return Confidence.LOW
    return Confidence.UNRATED


def assess_confidence(
    *,
    authority: SourceAuthority,
    reliability: SourceReliability,
    corroborating_sources: int,
) -> ConfidenceResult:
    """Assess confidence using provenance and corroboration."""
    reasons: list[str] = []

    authority_score = AUTHORITY_SCORES[authority]
    reliability_score = RELIABILITY_SCORES[reliability]
    corroboration_score = _corroboration_score(corroborating_sources)

    score = authority_score + reliability_score + corroboration_score
    score = min(score, 100)

    reasons.append(
        f"Source authority: {authority.name} (+{authority_score})"
    )

    reasons.append(
        f"Source reliability: {reliability.name} (+{reliability_score})"
    )

    reasons.append(
        f"Independent corroborating sources: "
        f"{corroborating_sources} (+{corroboration_score})"
    )

    level = _level_for_score(score)

    reasons.append(f"Confidence result: {level.name} ({score}/100)")

    return ConfidenceResult(
        level=level,
        score=score,
        reasons=tuple(reasons),
    )