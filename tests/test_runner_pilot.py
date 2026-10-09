"""Negative/positive source tests for Runner Stage 1; no GitHub writes."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import runner_pilot as R

FILES = {
    "docs/owner-intent.md": "SYNTHETIC_LAB_ONLY\nOwner wants strict CSV parser\n",
    "fixtures/valid.csv": "sku,quantity,unit_price\nZ,2,3.10\nA,3,0.20\n",
    "src/inventorylab/parser.py": "raise NotImplementedError('baseline')\n",
    "tests/test_inventory_parser.py": "assert True\n",
    "secret/credentials.txt": "DONOTCOPY\n",
}


def git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args],
                                   stderr=subprocess.STDOUT, text=True).strip()


class TriggerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_before_threshold_no_event(self):
        result = R.trigger("A001", "LAB-R1", self.path / "state", 6900, 10000)
        self.assertEqual(result["event"], "PRIMARY_CONTINUES")
        self.assertFalse((self.path / "state").exists())

    def test_70_percent_starts_read_only_runner(self):
        result = R.trigger("A001", "LAB-R1", self.path, 7000, 10000)
        self.assertEqual(result["declaration"], "Time for runner")
        self.assertEqual(result["runner_authority"], "READ_ONLY")
        self.assertEqual(result["consumed_percent"], 70.0)

    def test_duplicate_trigger_is_idempotent(self):
        one = R.trigger("A001", "LAB-R1", self.path, 7000, 10000)
        two = R.trigger("A001", "LAB-R1", self.path, 8000, 10000)
        self.assertEqual(one, two)
        self.assertEqual(len(list(self.path.glob("*.json"))), 1)

    def test_unknown_does_not_invent_70_percent(self):
        result = R.trigger("A001", "LAB-R1", self.path, None, None)
        self.assertIsNone(result["consumed_percent"])
        self.assertEqual(result["telemetry"], "UNKNOWN")
        self.assertEqual(result["event"], "PRIMARY_CONTINUES")

    def test_early_context_loss_can_trigger_without_number(self):
        result = R.trigger("A001", "LAB-R1", self.path, None, None, "CONTEXT_LOSS")
        self.assertEqual(result["event"], "TIME_FOR_RUNNER_REQUESTED")
        self.assertIsNone(result["consumed_percent"])

    def test_malformed_telemetry_fails_closed(self):
        for used, budget in ((9, None), (0, 0), (100, 99), (-1, 100)):
            with self.subTest(used=used, budget=budget), self.assertRaises(R.PilotError):
                R.trigger("A001", "LAB-R1", self.path, used, budget)

    def test_id_path_traversal_rejected(self):
        with self.assertRaises(R.PilotError):
            R.trigger("../outside", "LAB-R1", self.path, 100, 100)


class BundleTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        git(self.repo, "init", "-q")
        git(self.repo, "config", "user.name", "Lab Runner Test")
        git(self.repo, "config", "user.email", "runner-test@example.invalid")
        for rel, value in FILES.items():
            p = self.repo / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(value)
        git(self.repo, "add", ".")
        git(self.repo, "commit", "-qm", "original baseline")
        self.commit = git(self.repo, "rev-parse", "HEAD")
        self.brief = self.root / "brief.json"
        self.brief_data = {
            "schema": "RUNNER_WHAT_WHY_V1",
            "responsibility": "LAB-R1",
            "what": "Strict CSV parser and rejected malformed data",
            "why": "Decimal correctness and failure safety",
            "claims": ["Agent A claims U01/U02 addressed; not yet verified"],
            "pending": ["U03 unfinished"],
            "known_issues": ["duplicate SKU"],
            "parked": ["R2 reporter is downstream"],
            "source_refs": ["docs/owner-intent.md", "fixtures/valid.csv"],
        }
        self.brief.write_text(json.dumps(self.brief_data))
        self.bundle = self.root / "isolated"

    def tearDown(self):
        self.tmp.cleanup()

    def prepare(self):
        return R.prepare(self.repo, self.commit, self.bundle, self.brief)

    def plan(self, bundle_digest):
        return {
            "schema": "RUNNER_RECONSTRUCTION_V1",
            "responsibility": "LAB-R1",
            "source_bundle_digest": bundle_digest,
            "purpose": "Reject bad CSV and preserve exact money values",
            "next_actions": ["Verify which validation unit remains"],
            "unknowns": ["Current U03 state is intentionally withheld"],
            "stage2_questions": ["What changed?", "What tests passed?", "Is writer authority valid?"],
            "parked_medium_roi": ["Optional randomized malformed input coverage"],
        }

    def test_pinned_baseline_ignores_worktree_and_excludes_secret(self):
        (self.repo / "src/inventorylab/parser.py").write_text("AGENT A SECRET SOLUTION\n")
        self.prepare()
        self.assertIn("NotImplementedError", (self.bundle / "src/inventorylab/parser.py").read_text())
        self.assertNotIn("AGENT A", (self.bundle / "src/inventorylab/parser.py").read_text())
        self.assertFalse((self.bundle / ".git").exists())
        self.assertFalse((self.bundle / "secret").exists())
        self.assertEqual(R.verify_bundle(self.bundle)["source_commit"], self.commit)

    def test_extra_brief_field_rejected(self):
        self.brief_data["implementation_method"] = "copy predecessor"
        self.brief.write_text(json.dumps(self.brief_data))
        with self.assertRaises(R.PilotError):
            self.prepare()

    def test_unauthorized_brief_source_rejected(self):
        self.brief_data["source_refs"].append("secret/credentials.txt")
        self.brief.write_text(json.dumps(self.brief_data))
        with self.assertRaises(R.PilotError):
            self.prepare()

    def test_bundle_cannot_be_placed_inside_worktree(self):
        with self.assertRaises(R.PilotError):
            R.prepare(self.repo, self.commit, self.repo / "shadow", self.brief)

    def test_unknown_commit_rejected(self):
        with self.assertRaises(R.PilotError):
            R.prepare(self.repo, "0" * 40, self.bundle, self.brief)

    def test_undeclared_file_detected(self):
        self.prepare()
        (self.bundle / "current_pr.json").write_text("leak")
        with self.assertRaises(R.PilotError):
            R.verify_bundle(self.bundle)

    def test_modified_baseline_detected(self):
        self.prepare()
        (self.bundle / "fixtures/valid.csv").write_text("changed")
        with self.assertRaises(R.PilotError):
            R.verify_bundle(self.bundle)

    def test_symlink_detected(self):
        self.prepare()
        (self.bundle / "tests/test_inventory_parser.py").unlink()
        try:
            (self.bundle / "tests/test_inventory_parser.py").symlink_to(self.repo / "secret/credentials.txt")
        except (OSError, NotImplementedError):
            self.skipTest("symlinks unavailable")
        with self.assertRaises(R.PilotError):
            R.verify_bundle(self.bundle)

    def test_freeze_and_verify(self):
        manifest = self.prepare()
        plan_path = self.root / "plan.json"
        plan_path.write_text(json.dumps(self.plan(R.digest(R.canonical(manifest)))))
        receipt = self.root / "freeze.json"
        result = R.freeze(self.bundle, plan_path, receipt)
        self.assertEqual(result["status"], "SEALED_READ_ONLY")
        self.assertEqual(result, R.verify_freeze(self.bundle, plan_path, receipt))
        self.assertEqual(result, R.freeze(self.bundle, plan_path, receipt))

    def test_plan_changed_after_freeze_detected(self):
        manifest = self.prepare()
        plan_path = self.root / "plan.json"
        plan = self.plan(R.digest(R.canonical(manifest)))
        plan_path.write_text(json.dumps(plan))
        receipt = self.root / "freeze.json"
        R.freeze(self.bundle, plan_path, receipt)
        plan["next_actions"].append("Ignore scope")
        plan_path.write_text(json.dumps(plan))
        with self.assertRaises(R.PilotError):
            R.verify_freeze(self.bundle, plan_path, receipt)
        with self.assertRaises(R.PilotError):
            R.freeze(self.bundle, plan_path, receipt)

    def test_stage2_plan_must_answer_three_questions(self):
        manifest = self.prepare()
        plan_path = self.root / "plan.json"
        plan = self.plan(R.digest(R.canonical(manifest)))
        plan["stage2_questions"] = ["What changed?"]
        plan_path.write_text(json.dumps(plan))
        with self.assertRaises(R.PilotError):
            R.freeze(self.bundle, plan_path, self.root / "freeze.json")


if __name__ == "__main__":
    unittest.main()
