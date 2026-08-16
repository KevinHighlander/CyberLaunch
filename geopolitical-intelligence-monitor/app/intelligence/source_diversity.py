"""Source diversity assessment for CLIM."""

from __future__ import annotations

from dataclasses import dataclass

from app.models.source import IntelligenceSource


@dataclass(frozen=True, slots=True)
class SourceDiversityResult:
    """Summary of diversity across corroborating sources."""

    unique_sources: int
    unique_countries: int
    unique_source_types: int
    diversity_score: int
    reasons: tuple[str, ...]


def assess_source_diversity(
    sources: tuple[IntelligenceSource, ...],
) -> SourceDiversityResult:
    """Assess diversity across a set of intelligence sources."""
    if not sources:
        return SourceDiversityResult(
            unique_sources=0,
            unique_countries=0,
            unique_source_types=0,
            diversity_score=0,
            reasons=("No sources available.",),
        )

    unique_keys = {
        source.key
        for source in sources
    }

    unique_countries = {
        source.country
        for source in sources
        if source.country is not None
    }

    unique_types = {
        source.source_type
        for source in sources
    }

    score = 0
    reasons: list[str] = []

    source_count = len(unique_keys)
    country_count = len(unique_countries)
    type_count = len(unique_types)

    if source_count >= 3:
        score += 40
        reasons.append("Three or more unique sources.")
    elif source_count == 2:
        score += 25
        reasons.append("Two unique sources.")
    else:
        score += 10
        reasons.append("Only one unique source.")

    if country_count >= 3:
        score += 30
        reasons.append("Reporting spans three or more countries.")
    elif country_count == 2:
        score += 20
        reasons.append("Reporting spans two countries.")
    elif country_count == 1:
        score += 5
        reasons.append("Reporting comes from one country.")

    if type_count >= 3:
        score += 30
        reasons.append("Evidence includes three or more source types.")
    elif type_count == 2:
        score += 20
        reasons.append("Evidence includes two source types.")
    else:
        score += 5
        reasons.append("Evidence comes from one source type.")

    return SourceDiversityResult(
        unique_sources=source_count,
        unique_countries=country_count,
        unique_source_types=type_count,
        diversity_score=min(score, 100),
        reasons=tuple(reasons),
    )