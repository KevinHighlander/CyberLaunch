"""Top-level intelligence domains for CLIM."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class IntelligenceDomain:
    """A top-level area of intelligence analysis."""

    key: str
    display_name: str
    description: str


DOMAINS: dict[str, IntelligenceDomain] = {
    "geopolitics": IntelligenceDomain(
        key="geopolitics",
        display_name="Geopolitics",
        description=(
            "State behavior, military activity, diplomacy, alliances, "
            "territorial disputes, and international security."
        ),
    ),
    "cyber": IntelligenceDomain(
        key="cyber",
        display_name="Cyber",
        description=(
            "Cyberattacks, intrusion activity, malware, critical-infrastructure "
            "incidents, cyber policy, and state-linked cyber operations."
        ),
    ),
    "economics": IntelligenceDomain(
        key="economics",
        display_name="Economics",
        description=(
            "Sanctions, export controls, strategic trade, supply chains, "
            "energy security, and economically coercive state action."
        ),
    ),
    "infrastructure": IntelligenceDomain(
        key="infrastructure",
        display_name="Infrastructure",
        description=(
            "Critical infrastructure disruptions involving communications, "
            "energy, transportation, undersea cables, and other strategic systems."
        ),
    ),
    "space": IntelligenceDomain(
        key="space",
        display_name="Space",
        description=(
            "Military and civil space activity, satellite operations, "
            "counter-space capabilities, and space-related security developments."
        ),
    ),
    "information": IntelligenceDomain(
        key="information",
        display_name="Information Environment",
        description=(
            "Disinformation, influence operations, propaganda, information warfare, "
            "and coordinated manipulation of public information."
        ),
    ),
}


def get_domain(key: str) -> IntelligenceDomain | None:
    """Return a domain by key."""
    return DOMAINS.get(key)


def get_all_domains() -> tuple[IntelligenceDomain, ...]:
    """Return all registered intelligence domains."""
    return tuple(DOMAINS.values())