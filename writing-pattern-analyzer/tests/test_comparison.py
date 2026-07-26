import tempfile
import unittest
from pathlib import Path

from writing_pattern_analyzer.comparison import (
    compare_feature_values,
    compare_files,
    compare_texts,
)


class TestComparison(unittest.TestCase):

    def test_calculates_absolute_difference(self):
        result = compare_feature_values(5.8, 4.7)

        self.assertEqual(result["sample_a"], 5.8)
        self.assertEqual(result["sample_b"], 4.7)
        self.assertAlmostEqual(result["absolute_difference"], 1.1)

    def test_identical_text_has_zero_differences(self):
        result = compare_texts("Hello, world!", "Hello, world!")

        for feature in result.values():
            self.assertEqual(feature["absolute_difference"], 0.0)

    def test_excludes_document_size_counts(self):
        result = compare_texts("Short text.", "A longer sample appears here.")

        self.assertIn("average_word_length", result)
        self.assertNotIn("word_count", result)
        self.assertNotIn("sentence_count", result)

    def test_compares_text_files(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            path_a = Path(temporary_directory) / "sample_a.txt"
            path_b = Path(temporary_directory) / "sample_b.txt"

            path_a.write_text("A concise sample.", encoding="utf-8")
            path_b.write_text(
                "A somewhat longer writing sample!",
                encoding="utf-8",
            )

            result = compare_files(path_a, path_b)

            self.assertIn("vocabulary_richness", result)
            self.assertIn("exclamation_marks_per_100_words", result)


if __name__ == "__main__":
    unittest.main()

    