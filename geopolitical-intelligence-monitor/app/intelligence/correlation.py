"""Correlation engine for CLIM."""

from __future__ import annotations

import re
from dataclasses import dataclass

from app.models.normalized_event import NormalizedEvent


_STOP_WORDS = {
    "the",
    "a",
    "an",
    "of",
    "to",
    "and",
    "in",
    "on",
    "near",
    "around",
    "with",
    "for",
}


def _tokens(text: str) -> set[str]:
    """Return normalized keyword tokens."""
    words = re.findall(r"[a-z0-9]+", text.lower())

    return {
        word
        for word in words
        if word not in _STOP_WORDS
        and len(word) > 2
    }


@dataclass(frozen=True, slots=True)
class CorrelationResult:
    """Correlation assessment between two events."""

    score: float

    shared_terms: tuple[str, ...]

    is_match: bool


def correlate(
    left: NormalizedEvent,
    right: NormalizedEvent,
) -> CorrelationResult:
    """Compare two normalized events."""

    left_tokens = _tokens(
        left.analysis_text
    )

    right_tokens = _tokens(
        right.analysis_text
    )

    shared = sorted(
        left_tokens & right_tokens
    )

    union = left_tokens | right_tokens

    score = (
        len(shared) / len(union)
        if union
        else 0.0
    )

    return CorrelationResult(
        score=score,
        shared_terms=tuple(shared),
        is_match=score >= 0.40,
    )