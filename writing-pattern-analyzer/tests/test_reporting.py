import unittest

from writing_pattern_analyzer.reporting import (
    format_comparison_report,
    format_feature_name,
)


class TestReporting(unittest.TestCase):

    def test_formats_feature_name(self):
        result = format_feature_name("average_word_length")
        self.assertEqual(result, "Average Word Length")

    def test_formats_values_and_jointly_absent_features(self):
        comparison = {
            "vocabulary_richness": {
                "sample_a": 0.75,
                "sample_b": 0.80,
                "absolute_difference": 0.05,
                "similarity": 0.967741935,
            },
            "semicolons_per_100_words": {
                "sample_a": 0.0,
                "sample_b": 0.0,
                "absolute_difference": 0.0,
                "similarity": 1.0,
            },
        }

        result = format_comparison_report(
            comparison,
            "Formal",
            "Conversational",
        )

        self.assertIn("Writing Pattern Comparison", result)
        self.assertIn("Formal", result)
        self.assertIn("Conversational", result)
        self.assertIn("96.8%", result)
        self.assertIn("Not scored", result)

    def test_rejects_empty_comparison(self):
        with self.assertRaises(ValueError):
            format_comparison_report({})


if __name__ == "__main__":
    unittest.main()