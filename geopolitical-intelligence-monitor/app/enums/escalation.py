"""Escalation effects used by intelligence indicators."""

from __future__ import annotations

from enum import IntEnum


class Escalation(IntEnum):
    """Represents how an indicator changes regional tension."""

    DECREASE_MAJOR = -3
    DECREASE = -2
    DECREASE_MINOR = -1

    NEUTRAL = 0

    INCREASE_MINOR = 1
    INCREASE = 2
    INCREASE_MAJOR = 3