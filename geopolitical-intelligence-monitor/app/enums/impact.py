"""Impact levels for intelligence indicators."""

from __future__ import annotations

from enum import IntEnum


class Impact(IntEnum):
    """Relative importance of an intelligence indicator."""

    MINIMAL = 1
    LOW = 2
    MODERATE = 3
    HIGH = 4
    CRITICAL = 5