import json
from pathlib import Path
import unittest

from project import analyze


def example():
    return json.loads(Path(__file__).with_name("example.json").read_text(encoding="utf-8"))


class ProjectTests(unittest.TestCase):
    def test_peaks_and_ties(self):
        result = analyze(example())
        self.assertEqual(result["metrics"]["Peak voices"], 3)
        self.assertEqual(result["metrics"]["Equal-priority pairs"], 1)
        radio = next(row for row in result["rows"] if row["Cue"] == "Radio warning")
        self.assertIn("Balance with Alarm burst", radio["Mix note"])

    def test_adjacent_cues(self):
        data = {"cues": [{"id": str(i), "bus": "UI", "start": i, "duration": 1,
                          "priority": 2} for i in range(2)]}
        self.assertEqual(analyze(data)["metrics"]["Overlap pairs"], 0)
        self.assertEqual(analyze(data)["metrics"]["Peak voices"], 1)

    def test_long_bed_does_not_merge_separate_peaks(self):
        data = example()
        data["cues"] = [data["cues"][0], data["cues"][1], data["cues"][-1]]
        self.assertEqual(analyze(data)["metrics"]["Peak voices"], 2)

    def test_duplicate_id(self):
        data = example()
        data["cues"].append(data["cues"][0])
        with self.assertRaises(ValueError):
            analyze(data)

    def test_decimal_adjacent_timecodes(self):
        data = {"cues": [
            {"id": "one", "bus": "UI", "start": 0.1, "duration": 0.2, "priority": 1},
            {"id": "two", "bus": "UI", "start": 0.3, "duration": 0.4, "priority": 1},
        ]}
        self.assertEqual(analyze(data)["metrics"]["Overlap pairs"], 0)


if __name__ == "__main__":
    unittest.main()
