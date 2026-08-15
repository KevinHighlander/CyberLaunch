"""Confidence levels for intelligence assessments."""

from __future__ import annotations

from enum import Enum


class Confidence(Enum):
    """Assessment confidence."""

    UNRATED = "unrated"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very-high"