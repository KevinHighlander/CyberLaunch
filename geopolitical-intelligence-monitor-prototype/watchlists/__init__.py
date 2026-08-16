"""Geopolitical theater classification for CLIM."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class WatchMatch:
    watch: str
    display_name: str
    matched_terms: tuple[str, ...]


WATCHLISTS: dict[str, dict[str, object]] = {
    "taiwan": {
        "display_name": "Taiwan Strait",
        "terms": (
            "taiwan",
            "taipei",
            "taiwan strait",
            "pla",
            "people's liberation army",
            "kinmen",
            "matsu islands",
        ),
    },
    "korea": {
        "display_name": "Korean Peninsula",
        "terms": (
            "north korea",
            "south korea",
            "pyongyang",
            "seoul",
            "kim jong un",
            "korean peninsula",
            "dmz",
        ),
    },
    "iran": {
        "display_name": "Iran / Middle East",
        "terms": (
            "iran",
            "iranian",
            "tehran",
            "irgc",
            "strait of hormuz",
        ),
    },
    "russia-japan": {
        "display_name": "Russia–Japan / Kurils",
        "terms": (
            "russia",
            "russian",
            "moscow",
            "japan",
            "japanese",
            "tokyo",
            "kuril",
            "kurils",
            "iturup",
            "etorofu",
            "kunashir",
            "kunashiri",
            "shikotan",
            "habomai",
            "northern territories",
        ),
    },
}


def classify_watch(title: str, summary: str = "") -> WatchMatch | None:
    """Determine which CLIM watch area best matches an event."""
    text = f"{title} {summary}".lower()

    best_watch: str | None = None
    best_display = ""
    best_matches: set[str] = set()

    for watch, config in WATCHLISTS.items():
        terms = config["terms"]
        matches = {term for term in terms if term in text}

        if len(matches) > len(best_matches):
            best_watch = watch
            best_display = str(config["display_name"])
            best_matches = matches

    if best_watch is None:
        return None

    return WatchMatch(
        watch=best_watch,
        display_name=best_display,
        matched_terms=tuple(sorted(best_matches)),
    )
