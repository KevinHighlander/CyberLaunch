"""Deterministic intelligence briefing for CLIM."""

from __future__ import annotations

from app.intelligence.analyzer import AnalysisResult
from app.intelligence.fusion import FusedEvent
from app.ontology.entities import get_entity


def _display_name(
    entity_key: str,
) -> str:
    """Return a display name for an ontology entity key."""
    entity = get_entity(
        entity_key
    )

    if entity is not None:
        return entity.display_name

    return entity_key.replace(
        "-",
        " ",
    ).title()


def _append_analysis_sections(
    lines: list[str],
    analysis: AnalysisResult,
    *,
    summary: str,
) -> None:
    """Append common intelligence analysis sections."""
    lines.append("Summary")
    lines.append("-" * 54)
    lines.append(summary)
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
        lines.append(
            "Strategic Context"
        )
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


def build_brief(
    analysis: AnalysisResult,
) -> str:
    """Build a deterministic intelligence briefing."""
    lines: list[str] = []

    lines.append("=" * 54)
    lines.append(
        "CYBERLAUNCH INTELLIGENCE BRIEF"
    )
    lines.append("=" * 54)
    lines.append("")

    _append_analysis_sections(
        lines,
        analysis,
        summary=analysis.text,
    )

    lines.append("=" * 54)

    return "\n".join(
        lines
    )


def build_fused_brief(
    fused_event: FusedEvent,
) -> str:
    """Build a deterministic multi-source intelligence briefing."""
    lines: list[str] = []

    lines.append("=" * 54)
    lines.append(
        "CYBERLAUNCH FUSED INTELLIGENCE BRIEF"
    )
    lines.append("=" * 54)
    lines.append("")

    lines.append("Corroboration")
    lines.append("-" * 54)

    lines.append(
        f"Reports: "
        f"{fused_event.group.event_count}"
    )

    lines.append(
        f"Independent Sources: "
        f"{fused_event.source_count}"
    )

    lines.append(
        "Corroborated: "
        f"{'YES' if fused_event.is_corroborated else 'NO'}"
    )

    if fused_event.group.source_names:
        lines.append(
            "Sources: "
            + ", ".join(
                fused_event.group.source_names
            )
        )

    lines.append("")

    diversity = fused_event.source_diversity

    lines.append("Source Diversity")
    lines.append("-" * 54)

    lines.append(
        f"Score: "
        f"{diversity.diversity_score}/100"
    )

    lines.append(
        f"Unique Countries: "
        f"{diversity.unique_countries}"
    )

    lines.append(
        f"Source Types: "
        f"{diversity.unique_source_types}"
    )

    for reason in diversity.reasons:
        lines.append(
            f"• {reason}"
        )

    lines.append("")

    if fused_event.knowledge_neighborhoods:
        lines.append(
            "Knowledge Context"
        )
        lines.append("-" * 54)

        lines.append(
            "Background relationships only; "
            "not evidence of event involvement."
        )

        for neighborhood in fused_event.knowledge_neighborhoods:
            entity_name = _display_name(
                neighborhood.entity_key
            )

            neighbor_names = tuple(
                _display_name(
                    neighbor_key
                )
                for neighbor_key
                in neighborhood.neighbor_keys
            )

            if neighbor_names:
                lines.append(
                    f"• {entity_name}: "
                    + ", ".join(
                        neighbor_names
                    )
                )
            else:
                lines.append(
                    f"• {entity_name}: "
                    "no known neighbors"
                )

        lines.append("")

    _append_analysis_sections(
        lines,
        fused_event.analysis,
        summary=fused_event.summary,
    )

    lines.append("=" * 54)

    return "\n".join(
        lines
    )