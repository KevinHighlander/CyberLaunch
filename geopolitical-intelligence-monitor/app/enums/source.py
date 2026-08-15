"""Source metadata enums."""

from __future__ import annotations

from enum import Enum


class SourceAuthority(Enum):
    PRIMARY = "primary"
    SECONDARY = "secondary"
    UNKNOWN = "unknown"


class SourceReliability(Enum):
    OFFICIAL = "official"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"