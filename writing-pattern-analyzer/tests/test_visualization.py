import tempfile
import unittest
from pathlib import Path

from writing_pattern_analyzer.comparison import compare_texts
from writing_pattern_analyzer.visualization import (
    chart_similarity_percentage,
    create_similarity_chart,
)


class TestVisualization(unittest.TestCase):

    def test_creates_nonempty_png_file(self):
        comparison = compare_texts(
            "Formal writing uses structured language.",
            "Hey, this writing's pretty casual!",
        )

        with tempfile.TemporaryDirectory() as temporary_directory:
            output_path = (
                Path(temporary_directory)
                / "charts"
                / "similarity.png"
            )

            result = create_similarity_chart(
                comparison,
                output_path,
                "Formal",
                "Conversational",
            )

            self.assertEqual(result, output_path)
            self.assertTrue(output_path.exists())
            self.assertGreater(output_path.stat().st_size, 0)

    def test_rejects_empty_comparison(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            output_path = Path(temporary_directory) / "empty.png"

            with self.assertRaises(ValueError):
                create_similarity_chart({}, output_path)

    def test_jointly_absent_feature_is_not_scored(self):
        values = {
            "sample_a": 0.0,
            "sample_b": 0.0,
            "absolute_difference": 0.0,
            "similarity": 1.0,
        }

        self.assertIsNone(chart_similarity_percentage(values))

    def test_present_feature_returns_percentage(self):
        values = {
            "sample_a": 4.0,
            "sample_b": 6.0,
            "absolute_difference": 2.0,
            "similarity": 0.8,
        }

        self.assertAlmostEqual(
            chart_similarity_percentage(values),
            80.0,
        )


if __name__ == "__main__":
    unittest.main()