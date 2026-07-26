import unittest

from writing_pattern_analyzer.features import count_words, tokenize_words


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
if __name__ == "__main__":
    unittest.main()