import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from writing_pattern_analyzer.cli import (
    LIMITATION_NOTICE,
    build_parser,
    main,
)


class TestCommandLineInterface(unittest.TestCase):

    def test_parser_uses_expected_defaults(self):
        parser = build_parser()
        arguments = parser.parse_args(
            ["first.txt", "second.txt"]
        )

        self.assertEqual(arguments.sample_a, Path("first.txt"))
        self.assertEqual(arguments.sample_b, Path("second.txt"))
        self.assertEqual(arguments.name_a, "Sample A")
        self.assertEqual(arguments.name_b, "Sample B")
        self.assertEqual(
            arguments.output,
            Path("output/similarity.png"),
        )

    def test_main_creates_chart_and_prints_notice(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            sample_a = directory / "formal.txt"
            sample_b = directory / "conversational.txt"
            output_path = directory / "similarity.png"

            sample_a.write_text(
                "Formal writing uses structured terminology.",
                encoding="utf-8",
            )
            sample_b.write_text(
                "Hey, this writing's pretty casual!",
                encoding="utf-8",
            )

            captured_output = io.StringIO()

            with redirect_stdout(captured_output):
                exit_code = main(
                    [
                        str(sample_a),
                        str(sample_b),
                        "--name-a",
                        "Formal",
                        "--name-b",
                        "Conversational",
                        "--output",
                        str(output_path),
                    ]
                )

            self.assertEqual(exit_code, 0)
            self.assertTrue(output_path.exists())
            self.assertIn(
                str(output_path),
                captured_output.getvalue(),
            )
            self.assertIn(
                LIMITATION_NOTICE,
                captured_output.getvalue(),
            )

    def test_missing_file_exits_with_error(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            missing_a = directory / "missing-a.txt"
            missing_b = directory / "missing-b.txt"
            captured_error = io.StringIO()

            with redirect_stderr(captured_error):
                with self.assertRaises(SystemExit) as raised:
                    main([str(missing_a), str(missing_b)])

            self.assertEqual(raised.exception.code, 2)
            self.assertIn(
                "Unable to analyze samples",
                captured_error.getvalue(),
            )


if __name__ == "__main__":
    unittest.main()