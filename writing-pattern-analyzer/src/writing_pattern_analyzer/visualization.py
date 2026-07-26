from pathlib import Path

from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure


def chart_similarity_percentage(
    values: dict[str, float],
) -> float | None:
    """Return a percentage, or None when both feature values are zero."""
    if values["sample_a"] == 0 and values["sample_b"] == 0:
        return None

    return values["similarity"] * 100


def create_similarity_chart(
    comparison: dict[str, dict[str, float]],
    output_path: str | Path,
    sample_a_name: str = "Sample A",
    sample_b_name: str = "Sample B",
) -> Path:
    """Save a horizontal chart of per-feature similarities."""
    if not comparison:
        raise ValueError("Comparison data cannot be empty.")

    feature_names = [
        name.replace("_", " ").title()
        for name in comparison
    ]

    chart_percentages = [
        chart_similarity_percentage(values)
        for values in comparison.values()
    ]

    bar_lengths = [
        percentage if percentage is not None else 0.0
        for percentage in chart_percentages
    ]

    bar_colors = [
        "#287D8E" if percentage is not None else "#A0A0A0"
        for percentage in chart_percentages
    ]

    figure = Figure(figsize=(12, 7))
    FigureCanvasAgg(figure)
    axes = figure.subplots()

    bars = axes.barh(
        feature_names,
        bar_lengths,
        color=bar_colors,
    )

    axes.set_xlim(0, 100)
    axes.set_xlabel("Feature similarity (%)")
    axes.set_title(
        f"Writing Pattern Similarity\n"
        f"{sample_a_name} compared with {sample_b_name}"
    )
    axes.invert_yaxis()
    axes.xaxis.grid(True, linestyle="--", alpha=0.4)
    axes.set_axisbelow(True)

    for bar, percentage in zip(bars, chart_percentages):
        vertical_position = bar.get_y() + bar.get_height() / 2

        if percentage is None:
            axes.text(
                1,
                vertical_position,
                "Both values are 0 — not scored",
                va="center",
                ha="left",
                color="black",
            )
            continue

        if percentage >= 10:
            x_position = percentage - 1
            alignment = "right"
            text_color = "white"
        else:
            x_position = percentage + 1
            alignment = "left"
            text_color = "black"

        axes.text(
            x_position,
            vertical_position,
            f"{percentage:.1f}%",
            va="center",
            ha=alignment,
            color=text_color,
        )

    figure.tight_layout()

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(path, dpi=150)
    figure.clear()

    return path