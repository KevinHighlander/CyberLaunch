import json
import tempfile
import unittest
from pathlib import Path

import lecture_downloader as app


class LectureDownloaderTests(unittest.TestCase):
    def test_safe_name_blocks_path_characters(self):
        self.assertEqual(app.safe_name("../../Week: 1?.pdf"), "_.._Week_ 1_.pdf")

    def test_html_discovery_filters_extensions(self):
        html = '<a href="notes.pdf">Notes</a><a href="video.mp4">Video</a>'
        items = app.discover_html(html, "file:///tmp/index.html", {".pdf"}, set())
        self.assertEqual([item.url for item in items], ["file:///tmp/notes.pdf"])

    def test_rejects_non_https_and_unknown_hosts(self):
        with self.assertRaises(ValueError):
            app.validate_remote_url("http://files.example.edu/a.pdf", {"files.example.edu"})
        with self.assertRaises(ValueError):
            app.validate_remote_url("https://evil.example/a.pdf", {"files.example.edu"})

    def test_offline_manifest_download_and_deduplication(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "a.txt").write_text("same", encoding="utf-8")
            (root / "b.txt").write_text("same", encoding="utf-8")
            (root / "manifest.json").write_text(json.dumps({"files": ["a.txt", "b.txt"]}), encoding="utf-8")
            config = {
                "download_dir": "out",
                "state_file": "state.json",
                "extensions": [".txt"],
                "allowed_hosts": [],
                "courses": [{"name": "Test", "sources": [{"type": "manifest", "path": "manifest.json"}]}],
            }
            config_path = root / "config.json"
            config_path.write_text(json.dumps(config), encoding="utf-8")
            self.assertEqual(app.run(config_path), 0)
            self.assertEqual(len(list((root / "out" / "Test").glob("*.txt"))), 1)
            state = json.loads((root / "state.json").read_text(encoding="utf-8"))
            statuses = {entry["status"] for entry in state["urls"]["Test"].values()}
            self.assertEqual(statuses, {"downloaded", "duplicate"})

    def test_dry_run_does_not_write_state(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "file.txt").write_text("hello", encoding="utf-8")
            (root / "manifest.json").write_text('{"files":["file.txt"]}', encoding="utf-8")
            config = {"extensions": [".txt"], "courses": [{"name": "Test", "sources": [{"type": "manifest", "path": "manifest.json"}]}]}
            path = root / "config.json"
            path.write_text(json.dumps(config), encoding="utf-8")
            self.assertEqual(app.run(path, dry_run=True), 0)
            self.assertFalse((root / ".lecture-downloader-state.json").exists())


if __name__ == "__main__":
    unittest.main()
