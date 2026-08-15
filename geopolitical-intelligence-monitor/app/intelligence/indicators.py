"""Behavioral intelligence indicators for CLIM."""

from __future__ import annotations

from dataclasses import dataclass

from app.enums.escalation import Escalation
from app.enums.impact import Impact


@dataclass(frozen=True, slots=True)
class IntelligenceIndicator:
    """A recognizable action or condition with intelligence significance."""

    key: str
    display_name: str
    category: str
    description: str
    impact: Impact
    escalation: Escalation
    aliases: tuple[str, ...]


INDICATORS: dict[str, IntelligenceIndicator] = {
    "ballistic-missile-launch": IntelligenceIndicator(
        key="ballistic-missile-launch",
        display_name="Ballistic Missile Launch",
        category="military",
        description=(
            "Launch or confirmed firing of a ballistic missile, including "
            "short-, medium-, intermediate-, or intercontinental-range systems."
        ),
        impact=Impact.CRITICAL,
        escalation=Escalation.INCREASE_MAJOR,
        aliases=(
            "ballistic missile launch",
            "ballistic missile fired",
            "ballistic missile test",
            "icbm launch",
            "irbm launch",
            "mrbm launch",
            "srbm launch",
            "slbm launch",
        ),
    ),
    "cruise-missile-launch": IntelligenceIndicator(
        key="cruise-missile-launch",
        display_name="Cruise Missile Launch",
        category="military",
        description="Launch or confirmed firing of a cruise missile.",
        impact=Impact.HIGH,
        escalation=Escalation.INCREASE,
        aliases=(
            "cruise missile launch",
            "cruise missile fired",
            "cruise missile test",
        ),
    ),
    "military-exercise": IntelligenceIndicator(
        key="military-exercise",
        display_name="Military Exercise",
        category="military",
        description=(
            "Organized military training or drills involving operational forces."
        ),
        impact=Impact.MODERATE,
        escalation=Escalation.INCREASE_MINOR,
        aliases=(
            "military exercise",
            "military exercises",
            "military drill",
            "military drills",
            "war games",
            "live-fire exercise",
            "live fire exercise",
        ),
    ),
    "carrier-deployment": IntelligenceIndicator(
        key="carrier-deployment",
        display_name="Carrier Deployment",
        category="military",
        description=(
            "Deployment or repositioning of an aircraft carrier or carrier group."
        ),
        impact=Impact.HIGH,
        escalation=Escalation.INCREASE,
        aliases=(
            "carrier deployment",
            "aircraft carrier deployed",
            "carrier strike group deployed",
            "carrier strike group",
        ),
    ),
    "troop-mobilization": IntelligenceIndicator(
        key="troop-mobilization",
        display_name="Troop Mobilization",
        category="military",
        description=(
            "Large-scale mobilization, reinforcement, or movement of military forces."
        ),
        impact=Impact.CRITICAL,
        escalation=Escalation.INCREASE_MAJOR,
        aliases=(
            "troop mobilization",
            "military mobilization",
            "forces mobilized",
            "troops mobilized",
            "mass troop movement",
        ),
    ),
    "blockade": IntelligenceIndicator(
        key="blockade",
        display_name="Blockade",
        category="military",
        description=(
            "Attempt to prevent maritime, air, or other access to a territory."
        ),
        impact=Impact.CRITICAL,
        escalation=Escalation.INCREASE_MAJOR,
        aliases=(
            "blockade",
            "naval blockade",
            "air blockade",
            "maritime blockade",
        ),
    ),
    "air-intercept": IntelligenceIndicator(
        key="air-intercept",
        display_name="Air Intercept",
        category="military",
        description=(
            "Military aircraft intercepting or closely approaching another aircraft."
        ),
        impact=Impact.MODERATE,
        escalation=Escalation.INCREASE_MINOR,
        aliases=(
            "air intercept",
            "aircraft intercepted",
            "fighter jets intercepted",
            "fighter jet intercept",
        ),
    ),
    "naval-incursion": IntelligenceIndicator(
        key="naval-incursion",
        display_name="Naval Incursion",
        category="military",
        description=(
            "Naval activity entering or approaching contested or sensitive waters."
        ),
        impact=Impact.HIGH,
        escalation=Escalation.INCREASE,
        aliases=(
            "naval incursion",
            "entered territorial waters",
            "entered disputed waters",
            "warship entered",
        ),
    ),
    "critical-infrastructure-cyberattack": IntelligenceIndicator(
        key="critical-infrastructure-cyberattack",
        display_name="Critical Infrastructure Cyberattack",
        category="cyber",
        description=(
            "Cyberattack affecting strategic infrastructure such as energy, "
            "communications, transportation, government, or defense systems."
        ),
        impact=Impact.CRITICAL,
        escalation=Escalation.INCREASE,
        aliases=(
            "critical infrastructure cyberattack",
            "critical infrastructure cyber attack",
            "attack on critical infrastructure",
            "critical infrastructure hacked",
        ),
    ),
    "ransomware-attack": IntelligenceIndicator(
        key="ransomware-attack",
        display_name="Ransomware Attack",
        category="cyber",
        description="Confirmed ransomware activity against a monitored entity.",
        impact=Impact.HIGH,
        escalation=Escalation.INCREASE_MINOR,
        aliases=(
            "ransomware attack",
            "ransomware incident",
            "hit by ransomware",
        ),
    ),
    "ddos-attack": IntelligenceIndicator(
        key="ddos-attack",
        display_name="DDoS Attack",
        category="cyber",
        description="Distributed denial-of-service attack against a monitored target.",
        impact=Impact.MODERATE,
        escalation=Escalation.INCREASE_MINOR,
        aliases=(
            "ddos attack",
            "distributed denial of service",
            "denial-of-service attack",
        ),
    ),
    "data-breach": IntelligenceIndicator(
        key="data-breach",
        display_name="Data Breach",
        category="cyber",
        description="Unauthorized exposure or theft of protected information.",
        impact=Impact.MODERATE,
        escalation=Escalation.NEUTRAL,
        aliases=(
            "data breach",
            "data leak",
            "records stolen",
            "information exposed",
        ),
    ),
    "diplomatic-summit": IntelligenceIndicator(
        key="diplomatic-summit",
        display_name="Diplomatic Summit",
        category="diplomatic",
        description=(
            "High-level diplomatic meeting with potential strategic consequences."
        ),
        impact=Impact.HIGH,
        escalation=Escalation.DECREASE_MINOR,
        aliases=(
            "diplomatic summit",
            "leaders summit",
            "bilateral summit",
            "peace summit",
        ),
    ),
    "ceasefire": IntelligenceIndicator(
        key="ceasefire",
        display_name="Ceasefire",
        category="diplomatic",
        description="Agreement or declaration intended to halt active hostilities.",
        impact=Impact.CRITICAL,
        escalation=Escalation.DECREASE_MAJOR,
        aliases=(
            "ceasefire",
            "cease-fire",
            "halt in fighting",
            "cessation of hostilities",
        ),
    ),
    "sanctions": IntelligenceIndicator(
        key="sanctions",
        display_name="Sanctions",
        category="economic",
        description=(
            "New economic or political restrictions imposed against an entity."
        ),
        impact=Impact.HIGH,
        escalation=Escalation.INCREASE_MINOR,
        aliases=(
            "new sanctions",
            "economic sanctions",
            "sanctions imposed",
            "sanctions announced",
        ),
    ),
    "export-controls": IntelligenceIndicator(
        key="export-controls",
        display_name="Export Controls",
        category="economic",
        description=(
            "Restrictions on strategic exports, technology, or dual-use goods."
        ),
        impact=Impact.HIGH,
        escalation=Escalation.INCREASE_MINOR,
        aliases=(
            "export controls",
            "export restrictions",
            "technology export ban",
        ),
    ),
    "shipping-disruption": IntelligenceIndicator(
        key="shipping-disruption",
        display_name="Shipping Disruption",
        category="economic",
        description=(
            "Significant interference with maritime trade or strategic shipping routes."
        ),
        impact=Impact.HIGH,
        escalation=Escalation.INCREASE,
        aliases=(
            "shipping disruption",
            "shipping halted",
            "shipping suspended",
            "maritime traffic disrupted",
        ),
    ),
}


def get_indicator(key: str) -> IntelligenceIndicator | None:
    """Return an indicator by key."""
    return INDICATORS.get(key)


def get_all_indicators() -> tuple[IntelligenceIndicator, ...]:
    """Return all registered intelligence indicators."""
    return tuple(INDICATORS.values())


def find_indicators(text: str) -> tuple[IntelligenceIndicator, ...]:
    """Return indicators whose aliases appear in supplied text."""
    normalized = text.lower()

    matches = [
        indicator
        for indicator in INDICATORS.values()
        if any(alias in normalized for alias in indicator.aliases)
    ]

    return tuple(matches)


def get_indicators_by_category(
    category: str,
) -> tuple[IntelligenceIndicator, ...]:
    """Return all indicators in a category."""
    normalized = category.lower()

    return tuple(
        indicator
        for indicator in INDICATORS.values()
        if indicator.category == normalized
    )