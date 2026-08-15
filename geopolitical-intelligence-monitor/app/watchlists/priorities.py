"""Operational monitoring priorities for CLIM."""

from __future__ import annotations


THEATER_PRIORITIES: dict[str, int] = {
    "russia": 5,
    "indo-pacific": 5,
    "middle-east": 5,
    "europe": 4,
    "arctic": 4,
    "americas": 3,
    "africa": 3,
}


def get_theater_priority(theater_key: str) -> int:
    """Return the configured monitoring priority for a theater."""
    return THEATER_PRIORITIES.get(theater_key, 0)