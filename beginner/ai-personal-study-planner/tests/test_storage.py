import tempfile
import unittest
from pathlib import Path

from study_planner.storage import StorageError, load_json, save_json


class StorageTests(unittest.TestCase):
    def test_round_trip_and_no_temp_file_left(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "sub" / "x.json"
            save_json(p, {"a": [1, 2], "b": "é"})
            self.assertEqual(load_json(p), {"a": [1, 2], "b": "é"})
            self.assertEqual([f.name for f in p.parent.iterdir()], ["x.json"])

    def test_missing_returns_default(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(load_json(Path(d) / "nope.json", default=[]), [])

    def test_corrupt_file_raises(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "bad.json"
            p.write_text("{oops", encoding="utf-8")
            with self.assertRaises(StorageError):
                load_json(p)


if __name__ == "__main__":
    unittest.main()
