"""Explainable rule-based significance scoring for CLIM."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SignificanceResult:
    score: int
    category: str
    level: str
    matched_terms: tuple[str, ...]


CATEGORY_TERMS: dict[str, tuple[str, ...]] = {
    "military": (
        "military",
        "missile",
        "ballistic missile",
        "cruise missile",
        "nuclear",
        "warhead",
        "army",
        "navy",
        "air force",
        "aircraft",
        "fighter jet",
        "bomber",
        "warship",
        "destroyer",
        "submarine",
        "troops",
        "forces",
        "deployment",
        "deploys",
        "exercise",
        "exercises",
        "drill",
        "mobilization",
        "invasion",
        "blockade",
        "intercept",
        "artillery",
        "rocket",
        "drone",
    ),
    "diplomatic": (
        "sanctions",
        "summit",
        "diplomatic",
        "diplomacy",
        "ambassador",
        "ceasefire",
        "peace talks",
        "negotiations",
        "treaty",
        "alliance",
        "foreign minister",
        "defence minister",
        "defense minister",
    ),
    "cyber": (
        "cyberattack",
        "cyber attack",
        "cybersecurity",
        "hack",
        "hacked",
        "malware",
        "ransomware",
        "ddos",
        "phishing",
        "critical infrastructure",
        "data breach",
        "network intrusion",
    ),
    "economic-security": (
        "export controls",
        "trade restrictions",
        "semiconductor",
        "shipping",
        "strait",
        "oil supply",
        "energy security",
        "economic sanctions",
        "tariffs",
    ),
}

WATCH_TERMS = (
    "taiwan",
    "taipei",
    "taiwan strait",
    "north korea",
    "south korea",
    "pyongyang",
    "seoul",
    "iran",
    "tehran",
    "irgc",
    "russia",
    "russian",
    "japan",
    "japanese",
    "kuril",
    "iturup",
    "etorofu",
    "kunashir",
    "northern territories",
)

HIGH_IMPACT_TERMS = (
    "nuclear test",
    "nuclear weapon",
    "ballistic missile",
    "invasion",
    "blockade",
    "mobilization",
    "airstrike",
    "air strike",
    "missile launch",
    "military deployment",
    "troop deployment",
    "state of emergency",
    "martial law",
    "ceasefire",
    "declaration of war",
)


def score_event(title: str, summary: str = "") -> SignificanceResult:
    """Score an event with transparent, deterministic rules."""
    text = f"{title} {summary}".lower()
    score = 0
    matched: set[str] = set()
    category_scores: dict[str, int] = {}

    watch_matches = {term for term in WATCH_TERMS if term in text}
    if watch_matches:
        score += 2
        matched.update(watch_matches)

    for category, terms in CATEGORY_TERMS.items():
        hits = 0
        for term in terms:
            if term in text:
                hits += 1
                matched.add(term)
        if hits:
            category_scores[category] = hits
            score += min(hits, 3)

    for term in HIGH_IMPACT_TERMS:
        if term in text:
            score += 3
            matched.add(term)

    if (
        ("cyberattack" in text or "cyber attack" in text)
        and "critical infrastructure" in text
    ):
        score += 3

    if (
        any(term in text for term in ("kuril", "iturup", "etorofu", "kunashir"))
        and any(
            term in text
            for term in (
                "military",
                "forces",
                "troops",
                "deployment",
                "deploys",
                "exercise",
                "exercises",
            )
        )
    ):
        score += 3

    if "taiwan" in text and any(
        term in text for term in ("blockade", "invasion", "mobilization", "amphibious")
    ):
        score += 3

    if "north korea" in text and any(
        term in text
        for term in ("ballistic missile", "missile launch", "nuclear test", "nuclear weapon")
    ):
        score += 2

    if not watch_matches:
        score = min(score, 2)

    category = (
        max(category_scores, key=category_scores.get)
        if category_scores
        else "general"
    )

    if score >= 9:
        level = "critical-watch"
    elif score >= 6:
        level = "significant"
    elif score >= 3:
        level = "watch"
    else:
        level = "routine"

    return SignificanceResult(
        score=score,
        category=category,
        level=level,
        matched_terms=tuple(sorted(matched)),
    )
