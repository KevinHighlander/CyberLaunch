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
            lines.append(
                f"• {entity.display_name}"
            )

        lines.append("")

    if analysis.indicators:
        lines.append("Indicators")
        lines.append("-" * 54)

        for indicator in analysis.indicators:
            lines.append(
                f"• {indicator.display_name}"
            )

        lines.append("")

    if analysis.theaters:
        lines.append("Theaters")
        lines.append("-" * 54)

        for theater in analysis.theaters:
            lines.append(
                f"• {theater.display_name}"
            )

        lines.append("")

    if analysis.context.relationships:
        lines.append("Strategic Context")
        lines.append("-" * 54)

        for relationship in analysis.context.relationships:
            lines.append(
                "• "
                f"{relationship.source_name} ↔ "
                f"{relationship.target_name} — "
                f"{relationship.relationship}"
            )

            lines.append(
                f"  {relationship.description}"
            )

        lines.append("")

    lines.append("Assessment")
    lines.append("-" * 54)

    for line in analysis.reasoning:
        lines.append(
            f"• {line}"
        )

    lines.append("")
    lines.append("=" * 54)

    return "\n".join(lines)