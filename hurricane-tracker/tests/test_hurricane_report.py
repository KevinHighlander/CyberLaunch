"""Standard-library tests for the Atlantic Hurricane Tracker V2."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "hurricane-report.py"
SPEC = importlib.util.spec_from_file_location("hurricane_report", SCRIPT)
assert SPEC and SPEC.loader
hurricane_report = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(hurricane_report)


class ParserTests(unittest.TestCase):
    def test_outlook_probabilities_and_zones(self) -> None:
        systems = hurricane_report.parse_outlook(hurricane_report.SAMPLE_OUTLOOK_TEXT)
        self.assertEqual(len(systems), 1)
        self.assertEqual(systems[0]["probability_48h"], 10)
        self.assertEqual(systems[0]["probability_7d"], 40)
        self.assertEqual(systems[0]["zone"], "Africa and Cabo Verde Region")

    def test_tropical_wave_parsing(self) -> None:
        waves = hurricane_report.parse_tropical_waves(
            hurricane_report.SAMPLE_DISCUSSION_TEXT
        )
        self.assertEqual(len(waves), 1)
        self.assertEqual(waves[0]["longitude"], -25.0)
        self.assertIn("moving westward", waves[0]["movement"].lower())

    def test_live_discussion_heading_and_axis_format(self) -> None:
        discussion = """
        ...TROPICAL WAVES...

        A tropical wave is in the E Atlantic with axis across the Cabo Verde
        Islands near 25W, extending from 09N to 18N, and moving W at 10-15 kt.

        An Atlantic tropical wave is along 54W, extending from 09N to 21N, and
        moving W at 15-20 kt. Convection is between 57W and 61W.

        ...MONSOON TROUGH/ITCZ...
        """
        waves = hurricane_report.parse_tropical_waves(discussion)
        self.assertEqual(len(waves), 2)
        self.assertEqual([wave["longitude"] for wave in waves], [-25.0, -54.0])

    def test_only_atlantic_storms_are_kept(self) -> None:
        payload = {
            "activeStorms": hurricane_report.SAMPLE_STORMS["activeStorms"]
            + [{"id": "ep012026", "name": "Pacific Example"}]
        }
        storms = hurricane_report.parse_active_storms(payload)
        self.assertEqual([storm["name"] for storm in storms], ["Example"])

    def test_relevant_alert_filter(self) -> None:
        payload = {
            "features": hurricane_report.SAMPLE_ALERT["features"]
            + [{
                "id": "other",
                "properties": {
                    "id": "other",
                    "event": "Heat Advisory",
                    "headline": "Heat Advisory",
                },
            }]
        }
        alerts = hurricane_report.parse_alerts(payload, "FL")
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]["event"], "Tropical Storm Watch")


class EndToEndTests(unittest.TestCase):
    def test_sample_run_creates_all_required_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--sample",
                    "--output-dir",
                    temporary,
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("ALERT_REQUIRED=true", result.stdout)
            folder = Path(temporary)
            self.assertTrue((folder / "latest_report.txt").is_file())
            self.assertTrue(list(folder.glob("report_*.txt")))
            state_path = folder / "hurricane_state.json"
            self.assertTrue(state_path.is_file())
            state = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertEqual(state["schema_version"], 2)
            report = (folder / "latest_report.txt").read_text(encoding="utf-8")
            self.assertIn("30-SECOND QUICK LOOK", report)
            self.assertIn("ATLANTIC ZONES", report)
            self.assertIn("OFFLINE DEMONSTRATION", report)


if __name__ == "__main__":
    unittest.main()
