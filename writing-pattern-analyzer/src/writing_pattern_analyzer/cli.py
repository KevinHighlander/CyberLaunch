import argparse
from pathlib import Path

from .comparison import compare_files
from .visualization import create_similarity_chart
from .reporting import format_comparison_report


LIMITATION_NOTICE = (
    "Educational use only: feature similarity cannot determine whether text "
    "was AI-generated, establish authorship, or prove misconduct."
)


def build_parser() -> argparse.ArgumentParser:
    """Create and return the command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog="writing-pattern-analyzer",
        description=(
            "Compare selected stylometric features in two text files "
            "and create a similarity chart."
        ),
    )

    parser.add_argument(
        "sample_a",
        type=Path,
        help="Path to the first .txt writing sample.",
    )
    parser.add_argument(
        "sample_b",
        type=Path,
        help="Path to the second .txt writing sample.",
    )
    parser.add_argument(
        "--name-a",
        default="Sample A",
        help="Display name for the first sample.",
    )
    parser.add_argument(
        "--name-b",
        default="Sample B",
        help="Display name for the second sample.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("output/similarity.png"),
        help="Location for the generated PNG chart.",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the command-line application."""
    parser = build_parser()
    arguments = parser.parse_args(argv)

    try:
        comparison = compare_files(
            arguments.sample_a,
            arguments.sample_b,
        )
        chart_path = create_similarity_chart(
            comparison,
            arguments.output,
            arguments.name_a,
            arguments.name_b,
        )
    except (OSError, ValueError) as error:
        parser.error(f"Unable to analyze samples: {error}")

    report = format_comparison_report(
        comparison,
        arguments.name_a,
        arguments.name_b,
    )

    print(report)
    print()
    print(f"Chart saved to: {chart_path}")
    print(LIMITATION_NOTICE)

    return 0