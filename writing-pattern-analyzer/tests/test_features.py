import unittest

from writing_pattern_analyzer.features import (
    average_sentence_length,
    count_unique_words,
    average_word_length,
    count_words,
    tokenize_sentences,
    tokenize_words,
    vocabulary_richness,
    punctuation_counts,
    punctuation_rates,
    count_sentences,
    extract_features,
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

class TestPunctuationFeatures(unittest.TestCase):

    def test_counts_selected_punctuation(self):
        result = punctuation_counts("Wait, don't re-enter; really?!")

        self.assertEqual(result["commas"], 1)
        self.assertEqual(result["semicolons"], 1)
        self.assertEqual(result["question_marks"], 1)
        self.assertEqual(result["exclamation_marks"], 1)
        self.assertEqual(result["apostrophes"], 1)
        self.assertEqual(result["hyphens"], 1)

    def test_counts_curly_apostrophe(self):
        result = punctuation_counts("It’s fine.")
        self.assertEqual(result["apostrophes"], 1)
        self.assertEqual(result["periods"], 1)

    def test_normalizes_punctuation_per_100_words(self):
        result = punctuation_rates("One, two three four.")
        self.assertAlmostEqual(result["commas"], 25.0)
        self.assertAlmostEqual(result["periods"], 25.0)

    def test_empty_text_has_zero_rates(self):
        result = punctuation_rates("")
        self.assertTrue(all(rate == 0.0 for rate in result.values()))

class TestFeatureExtraction(unittest.TestCase):

    def test_counts_sentences(self):
        result = count_sentences("One sentence. Another sentence!")
        self.assertEqual(result, 2)

    def test_extracts_complete_profile(self):
        result = extract_features("Hello, world! Hello again.")

        self.assertEqual(result["word_count"], 4)
        self.assertEqual(result["unique_word_count"], 3)
        self.assertEqual(result["sentence_count"], 2)
        self.assertAlmostEqual(result["vocabulary_richness"], 0.75)
        self.assertAlmostEqual(result["average_word_length"], 5.0)
        self.assertAlmostEqual(result["average_sentence_length"], 2.0)
        self.assertAlmostEqual(result["commas_per_100_words"], 25.0)

    def test_extracts_empty_profile_safely(self):
        result = extract_features("")

        self.assertEqual(result["word_count"], 0)
        self.assertEqual(result["sentence_count"], 0)
        self.assertEqual(result["vocabulary_richness"], 0.0)
        self.assertEqual(result["average_word_length"], 0.0)
                
if __name__ == "__main__":
    unittest.main()