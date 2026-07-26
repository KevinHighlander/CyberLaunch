import unittest

from writing_pattern_analyzer.features import (
    average_sentence_length,
    count_unique_words,
    average_word_length,
    count_words,
    tokenize_sentences,
    tokenize_words,
    vocabulary_richness,
)

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

class TestSentenceFeatures(unittest.TestCase):

    def test_tokenizes_different_endings(self):
        result = tokenize_sentences("Hello! How are you? I am well.")
        self.assertEqual(result, ["Hello", "How are you", "I am well"])

    def test_ignores_repeated_punctuation(self):
        result = tokenize_sentences("Really?! Yes!!!")
        self.assertEqual(result, ["Really", "Yes"])

    def test_calculates_average_sentence_length(self):
        result = average_sentence_length(
            "Birds fly. Some birds fly south."
        )
        self.assertAlmostEqual(result, 3.0)

    def test_empty_text_has_zero_average(self):
        result = average_sentence_length("")
        self.assertEqual(result, 0.0)

class TestWordLengthFeatures(unittest.TestCase):

    def test_calculates_average_word_length(self):
        result = average_word_length("Cat runs.")
        self.assertAlmostEqual(result, 3.5)

    def test_ignores_internal_punctuation(self):
        result = average_word_length("Don't re-use code.")
        self.assertAlmostEqual(result, 13 / 3)

    def test_empty_text_has_zero_average(self):
        result = average_word_length("")
        self.assertEqual(result, 0.0)

if __name__ == "__main__":
    unittest.main()