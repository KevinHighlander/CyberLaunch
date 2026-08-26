"""Confidence assessment for CLIM intelligence events."""

from __future__ import annotations

from dataclasses import dataclass

from app.enums.confidence import Confidence
from app.enums.source import SourceAuthority, SourceReliability
from app.models.normalized_event import NormalizedEvent


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


def _corroboration_score(
    source_count: int,
) -> int:
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


def _level_for_score(
    score: int,
) -> Confidence:
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

    authority_score = AUTHORITY_SCORES[
        authority
    ]

    reliability_score = RELIABILITY_SCORES[
        reliability
    ]

    corroboration_score = _corroboration_score(
        corroborating_sources
    )

    score = (
        authority_score
        + reliability_score
        + corroboration_score
    )

    score = min(
        score,
        100,
    )

    reasons.append(
        f"Source authority: "
        f"{authority.name} "
        f"(+{authority_score})"
    )

    reasons.append(
        f"Source reliability: "
        f"{reliability.name} "
        f"(+{reliability_score})"
    )

    reasons.append(
        "Independent corroborating sources: "
        f"{corroborating_sources} "
        f"(+{corroboration_score})"
    )

    level = _level_for_score(
        score
    )

    reasons.append(
        f"Confidence result: "
        f"{level.name} "
        f"({score}/100)"
    )

    return ConfidenceResult(
        level=level,
        score=score,
        reasons=tuple(
            reasons
        ),
    )


def _unique_source_profiles(
    events: tuple[NormalizedEvent, ...],
) -> dict[
    str,
    tuple[
        SourceAuthority,
        SourceReliability,
    ],
]:
    """
    Return conservative provenance profiles for unique sources.

    Repeated reports from the same source count once. If duplicate
    reports contain inconsistent provenance metadata, CLIM retains the
    more conservative authority and reliability values.
    """
    profiles: dict[
        str,
        tuple[
            SourceAuthority,
            SourceReliability,
        ],
    ] = {}

    for event in events:
        existing = profiles.get(
            event.source_name
        )

        if existing is None:
            profiles[
                event.source_name
            ] = (
                event.source_authority,
                event.source_reliability,
            )
            continue

        existing_authority, existing_reliability = (
            existing
        )

        authority = min(
            (
                existing_authority,
                event.source_authority,
            ),
            key=lambda value: AUTHORITY_SCORES[
                value
            ],
        )

        reliability = min(
            (
                existing_reliability,
                event.source_reliability,
            ),
            key=lambda value: RELIABILITY_SCORES[
                value
            ],
        )

        profiles[
            event.source_name
        ] = (
            authority,
            reliability,
        )

    return profiles


def assess_fused_confidence(
    events: tuple[NormalizedEvent, ...],
) -> ConfidenceResult:
    """Assess confidence across multiple correlated reports."""
    profiles = _unique_source_profiles(
        events
    )

    if not profiles:
        return ConfidenceResult(
            level=Confidence.UNRATED,
            score=0,
            reasons=(
                "No source provenance available.",
                "Confidence result: UNRATED (0/100)",
            ),
        )

    authority_scores = [
        AUTHORITY_SCORES[
            authority
        ]
        for authority, _ in profiles.values()
    ]

    reliability_scores = [
        RELIABILITY_SCORES[
            reliability
        ]
        for _, reliability in profiles.values()
    ]

    source_count = len(
        profiles
    )

    authority_score = (
        sum(authority_scores)
        // source_count
    )

    reliability_score = (
        sum(reliability_scores)
        // source_count
    )

    corroboration_score = _corroboration_score(
        source_count
    )

    score = (
        authority_score
        + reliability_score
        + corroboration_score
    )

    score = min(
        score,
        100,
    )

    reasons: list[str] = [
        (
            "Average source authority "
            f"contribution: +{authority_score}"
        ),
        (
            "Average source reliability "
            f"contribution: +{reliability_score}"
        ),
        (
            "Independent corroborating sources: "
            f"{source_count} "
            f"(+{corroboration_score})"
        ),
    ]

    if len(events) > source_count:
        reasons.append(
            "Duplicate reports from the same source "
            "did not increase corroboration."
        )

    level = _level_for_score(
        score
    )

    reasons.append(
        f"Confidence result: "
        f"{level.name} "
        f"({score}/100)"
    )

    return ConfidenceResult(
        level=level,
        score=score,
        reasons=tuple(
            reasons
        ),
    )