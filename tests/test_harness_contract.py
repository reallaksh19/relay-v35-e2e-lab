import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ScaffoldContract(unittest.TestCase):
    def test_synthetic_owner_label_is_explicit(self):
        text = (ROOT / "docs/owner-intent.md").read_text(encoding="utf-8")
        self.assertIn("SYNTHETIC", text)
        self.assertIn("NOT_AUTHENTICATED_CHAT_SOURCE", text)

    def test_no_writer_in_workflow(self):
        text = (ROOT / ".github/workflows/inventory.yml").read_text(encoding="utf-8")
        self.assertIn("contents: read", text)
        self.assertNotIn("pull-requests: write", text)
        self.assertNotIn("issues: write", text)

    def test_scenarios_and_unimplemented_marker(self):
        text = (ROOT / "docs/stress-matrix.md").read_text(encoding="utf-8")
        for n in range(1, 17):
            self.assertIn(f"S{n:02d}", text)
        self.assertIn("NotImplementedError", (ROOT / "src/inventorylab/parser.py").read_text())
        self.assertIn("NotImplementedError", (ROOT / "src/inventorylab/report.py").read_text())
