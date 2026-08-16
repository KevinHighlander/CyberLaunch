"""Deterministic intelligence briefing for CLIM."""

from __future__ import annotations

from app.intelligence.analyzer import AnalysisResult


def build_brief(
    analysis: AnalysisResult,
) -> str:
    """Build a deterministic intelligence briefing."""

    lines: list[str] = []

    lines.append("=" * 54)
    lines.append("CYBERLAUNCH INTELLIGENCE BRIEF")
    lines.append("=" * 54)
    lines.append("")

    lines.append("Summary")
    lines.append("-" * 54)
    lines.append(analysis.text)
    lines.append("")

    lines.append("Confidence")
    lines.append("-" * 54)
    lines.append(
        f"{analysis.confidence.level.name} "
        f"({analysis.confidence.score}/100)"
    )
    lines.append("")

    if analysis.entities:
        lines.append("Entities")
        lines.append("-" * 54)

        for entity in analysis.entities:
            lines.append(f"• {entity.display_name}")

        lines.append("")

    if analysis.indicators:
        lines.append("Indicators")
        lines.append("-" * 54)

        for indicator in analysis.indicators:
            lines.append(f"• {indicator.display_name}")

        lines.append("")

    if analysis.theaters:
        lines.append("Theaters")
        lines.append("-" * 54)

        for theater in analysis.theaters:
            lines.append(f"• {theater.display_name}")

        lines.append("")

    relationship_lines = [
        line
        for line in analysis.reasoning
        if line.startswith("Known relationship:")
    ]

    if relationship_lines:
        lines.append("Strategic Context")
        lines.append("-" * 54)

        for line in relationship_lines:
            lines.append(
                line.replace(
                    "Known relationship: ",
                    "• ",
                )
            )

        lines.append("")

    lines.append("Assessment")
    lines.append("-" * 54)

    for line in analysis.reasoning:
        if line.startswith("Known relationship:"):
            continue

        lines.append(f"• {line}")

    lines.append("")
    lines.append("=" * 54)

    return "\n".join(lines)