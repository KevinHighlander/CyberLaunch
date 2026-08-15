"""Watch-area registry and classification."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class WatchMatch:
    key: str
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
    """Return the strongest matching CLIM watch area."""
    text = f"{title} {summary}".lower()
    best: WatchMatch | None = None

    for key, config in WATCHLISTS.items():
        terms = tuple(config["terms"])
        matches = tuple(sorted(term for term in terms if term in text))
        if not matches:
            continue

        candidate = WatchMatch(
            key=key,
            display_name=str(config["display_name"]),
            matched_terms=matches,
        )
        if best is None or len(candidate.matched_terms) > len(best.matched_terms):
            best = candidate

    return best
