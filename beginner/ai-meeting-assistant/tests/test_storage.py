import json
import tempfile
import unittest
from pathlib import Path

from meeting_assistant.storage import StorageError, read_text, save_json, save_text


class StorageTests(unittest.TestCase):
    def test_round_trip_and_no_temp_left(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "sub" / "x.json"
            save_json(p, {"a": "é"})
            self.assertEqual(json.loads(p.read_text(encoding="utf-8")), {"a": "é"})
            self.assertEqual([f.name for f in p.parent.iterdir()], ["x.json"])

    def test_read_text_errors(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(StorageError):
                read_text(Path(d) / "missing.txt")
            big = Path(d) / "big.txt"
            save_text(big, "x" * 50)
            with self.assertRaises(StorageError):
                read_text(big, max_chars=10)
            binary = Path(d) / "bin.txt"
            binary.write_bytes(b"\xff\xfe\x00bad")
            with self.assertRaises(StorageError):
                read_text(binary)


if __name__ == "__main__":
    unittest.main()
