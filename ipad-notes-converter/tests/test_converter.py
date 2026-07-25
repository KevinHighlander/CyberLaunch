import json
import logging
import tempfile
import unittest
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from MAIN import (  # noqa: E402
    load_settings,
    process_file,
    safe_component,
    subject_for,
    unique_path,
)


class ConverterTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.inbox = self.root / "inbox"
        self.destination = self.root / "output"
        self.inbox.mkdir()
        config = {
            "inbox": str(self.inbox),
            "destination": str(self.destination),
            "settle_seconds": 0,
            "subjects": {
                "Math": {"folder": "Math Assignments", "keywords": ["calculus", "algebra"]}
            },
        }
        self.config_path = self.root / "config.json"
        self.config_path.write_text(json.dumps(config), encoding="utf-8")
        self.settings = load_settings(self.config_path)
        self.logger = logging.getLogger(f"test-{id(self)}")
        self.logger.addHandler(logging.NullHandler())

    def tearDown(self):
        self.temporary.cleanup()

    def test_prefix_routing_removes_prefix(self):
        folder, stem = subject_for("Math - Homework 3.pdf", self.settings)
        self.assertEqual(folder, "Math Assignments")
        self.assertEqual(stem, "Homework 3")

    def test_keyword_routing(self):
        folder, stem = subject_for("calculus review.pdf", self.settings)
        self.assertEqual(folder, "Math Assignments")
        self.assertEqual(stem, "calculus review")

    def test_default_routing(self):
        folder, _ = subject_for("Shopping list.pdf", self.settings)
        self.assertEqual(folder, "_Unsorted")

    def test_safe_component_removes_path_characters(self):
        cleaned = safe_component("../Math/Homework")
        self.assertEqual(cleaned, "-Math-Homework")
        self.assertNotIn("/", cleaned)
        self.assertNotIn("..", cleaned)

    def test_unique_path_numbers_duplicates(self):
        path = self.destination / "Note.pdf"
        path.parent.mkdir()
        path.touch()
        self.assertEqual(unique_path(path).name, "Note (2).pdf")

    def test_pdf_is_copied_and_source_removed(self):
        source = self.inbox / "Math - Quiz.pdf"
        source.write_bytes(b"%PDF-1.4\nexample")
        target = process_file(source, self.settings, self.logger)
        self.assertEqual(target, self.destination / "Math Assignments" / "Quiz.pdf")
        self.assertTrue(target.exists())
        self.assertFalse(source.exists())

    def test_dry_run_keeps_source(self):
        source = self.inbox / "Math - Quiz.pdf"
        source.write_bytes(b"%PDF-1.4\nexample")
        target = process_file(source, self.settings, self.logger, dry_run=True)
        self.assertTrue(source.exists())
        self.assertFalse(target.exists())

    def test_unsupported_file_moves_to_quarantine(self):
        source = self.inbox / "archive.zip"
        source.write_bytes(b"zip")
        target = process_file(source, self.settings, self.logger)
        self.assertEqual(target.parent.name, "Unsupported")
        self.assertTrue(target.exists())
        self.assertFalse(source.exists())

    def test_refuses_file_outside_inbox(self):
        source = self.root / "outside.pdf"
        source.write_bytes(b"%PDF")
        self.assertIsNone(process_file(source, self.settings, self.logger))
        self.assertTrue(source.exists())


if __name__ == "__main__":
    unittest.main()
