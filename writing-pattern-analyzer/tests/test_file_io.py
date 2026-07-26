import tempfile
import unittest
from pathlib import Path

from writing_pattern_analyzer.file_io import load_text_file


class TestLoadTextFile(unittest.TestCase):

    def test_loads_utf8_text_file(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "sample.txt"
            path.write_text("Café writing sample.", encoding="utf-8")

            result = load_text_file(path)

            self.assertEqual(result, "Café writing sample.")

    def test_rejects_non_text_file(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "sample.pdf"

            with self.assertRaises(ValueError):
                load_text_file(path)

    def test_missing_file_raises_error(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "missing.txt"

            with self.assertRaises(FileNotFoundError):
                load_text_file(path)


if __name__ == "__main__":
    unittest.main()