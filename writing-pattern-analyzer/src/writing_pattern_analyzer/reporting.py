def format_feature_name(feature_name: str) -> str:
    """Convert an internal feature name into a readable label."""
    return feature_name.replace("_", " ").title()


def format_comparison_report(
    comparison: dict[str, dict[str, float]],
    sample_a_name: str = "Sample A",
    sample_b_name: str = "Sample B",
) -> str:
    """Return a readable table comparing two feature profiles."""
    if not comparison:
        raise ValueError("Comparison data cannot be empty.")

    lines = [
        "Writing Pattern Comparison",
        f"{sample_a_name} compared with {sample_b_name}",
        "",
        (
            f"{'Feature':<36}"
            f"{sample_a_name:>14}"
            f"{sample_b_name:>14}"
            f"{'Similarity':>14}"
        ),
        "-" * 78,
    ]

    for feature_name, values in comparison.items():
        readable_name = format_feature_name(feature_name)
        sample_a = values["sample_a"]
        sample_b = values["sample_b"]

        if sample_a == 0 and sample_b == 0:
            similarity = "Not scored"
        else:
            similarity = f"{values['similarity'] * 100:.1f}%"

        lines.append(
            f"{readable_name:<36}"
            f"{sample_a:>14.3f}"
            f"{sample_b:>14.3f}"
            f"{similarity:>14}"
        )

    return "\n".join(lines)