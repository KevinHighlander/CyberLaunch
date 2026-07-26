import tempfile
import unittest
from pathlib import Path

from writing_pattern_analyzer.comparison import (
    calculate_feature_similarity,
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

    def test_identical_values_have_full_similarity(self):
        result = calculate_feature_similarity(5.0, 5.0)
        self.assertEqual(result, 1.0)

    def test_zero_and_positive_value_have_no_similarity(self):
        result = calculate_feature_similarity(0.0, 5.0)
        self.assertEqual(result, 0.0)

    def test_two_zero_values_match(self):
        result = calculate_feature_similarity(0.0, 0.0)
        self.assertEqual(result, 1.0)

    def test_similarity_is_scale_independent(self):
        small_scale = calculate_feature_similarity(4.0, 6.0)
        large_scale = calculate_feature_similarity(40.0, 60.0)

        self.assertAlmostEqual(small_scale, 0.8)
        self.assertAlmostEqual(large_scale, 0.8)

if __name__ == "__main__":
    unittest.main()