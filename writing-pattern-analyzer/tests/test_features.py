import unittest

from writing_pattern_analyzer.features import ( count_unique_words, count_words, tokenize_words, vocabulary_richness,)


class TestCountWords(unittest.TestCase):

    def test_simple_sentence(self):
        result = count_words("Stylometry examines writing patterns.")
        self.assertEqual(result, 4)

    def test_empty_text(self):
        result = count_words("")
        self.assertEqual(result, 0)

    def test_extra_whitespace(self):
        result = count_words("One   two\nthree")
        self.assertEqual(result, 3)

class TestTokenizeWords(unittest.TestCase):

    def test_removes_surrounding_punctuation(self):
        result = tokenize_words("Hello, world!")
        self.assertEqual(result, ["hello", "world"])

    def test_standardizes_capitalization(self):
        result = tokenize_words("Python PYTHON python")
        self.assertEqual(result, ["python", "python", "python"])

    def test_preserves_internal_punctuation(self):
        result = tokenize_words("Don't ignore well-written work.")
        self.assertEqual(
            result,
            ["don't", "ignore", "well-written", "work"],
        )

class TestVocabularyFeatures(unittest.TestCase):

    def test_counts_unique_words(self):
        result = count_unique_words("The dog chased the dog.")
        self.assertEqual(result, 3)

    def test_calculates_vocabulary_richness(self):
        result = vocabulary_richness("The dog chased the ball.")
        self.assertAlmostEqual(result, 0.8)

    def test_empty_text_has_zero_richness(self):
        result = vocabulary_richness("")
        self.assertEqual(result, 0.0)

    def test_whitespace_has_zero_richness(self):
        result = vocabulary_richness("   \n\t")
        self.assertEqual(result, 0.0) 

if __name__ == "__main__":
    unittest.main()