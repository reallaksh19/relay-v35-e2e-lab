"""RNR-04 actual Git/remote reconciliation negative oracles; no provider write."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import runner_pilot as S1
import runner_stage2 as S2

BASE = {
    "docs/owner-intent.md": "SYNTHETIC_LAB_ONLY\nstrict CSV, parser separate from reporter\n",
    "fixtures/valid.csv": "sku,quantity,unit_price\nZ,2,3.10\nA,3,0.20\n",
    "src/inventorylab/parser.py": "raise NotImplementedError('baseline')\n",
    "tests/test_inventory_parser.py": "assert True\n",
    "src/inventorylab/report.py": "report must remain separately governed\n",
}


def git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args], stderr=subprocess.STDOUT, text=True).strip()


class Stage2Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        git(self.repo, "init", "-q", "-b", "main")
        git(self.repo, "config", "user.name", "Isolated Test")
        git(self.repo, "config", "user.email", "test@example.invalid")
        for name, contents in BASE.items():
            f = self.repo / name
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text(contents)
        git(self.repo, "add", ".")
        git(self.repo, "commit", "-qm", "baseline")
        self.base = git(self.repo, "rev-parse", "HEAD")
        self.remote = self.root / "remote.git"
        subprocess.check_call(["git", "init", "-q", "--bare", str(self.remote)])
        git(self.repo, "remote", "add", "origin", str(self.remote))
        git(self.repo, "push", "-q", "-u", "origin", "main")
        self.brief = self.root / "brief.json"
        self.brief.write_text(json.dumps({
            "schema": "RUNNER_WHAT_WHY_V1", "responsibility": "LAB-R1",
            "what": "Strict CSV parser", "why": "Fail-closed input validation",
            "claims": ["Agent A claims U01/U02 done"], "pending": ["U03"],
            "known_issues": ["nonfinite price"], "parked": ["R2 reporter"],
            "source_refs": ["docs/owner-intent.md", "fixtures/valid.csv"]}))
        self.bundle = self.root / "bundle"
        manifest = S1.prepare(self.repo, self.base, self.bundle, self.brief)
        self.plan = self.root / "plan.json"
        self.plan_data = {
            "schema": "RUNNER_RECONSTRUCTION_V1", "responsibility": "LAB-R1",
            "source_bundle_digest": S1.digest(S1.canonical(manifest)),
            "purpose": "Validated CSV parsing", "next_actions": ["Verify and implement remaining parser unit"],
            "unknowns": ["Current candidate and real test acceptance withheld"],
            "stage2_questions": ["What changed?", "What is verified?", "Any scope drift?"],
            "parked_medium_roi": ["Additional malformed CSV fuzzing"],
        }
        self.plan.write_text(json.dumps(self.plan_data))
        self.receipt = self.root / "receipt.json"
        S1.freeze(self.bundle, self.plan, self.receipt)
        self.handover = self.root / "handover.json"

    def tearDown(self):
        self.tmp.cleanup()

    def current_head(self):
        return git(self.repo, "rev-parse", "HEAD")

    def predecessor(self, **overrides):
        data = {
            "schema": "RUNNER_PRIMARY_HANDOVER_V1", "responsibility": "LAB-R1",
            "starting_commit": self.base, "candidate_head": self.current_head(),
            "branch": "main", "proposed_next_responsibility": "LAB-R1",
            "proposed_plan": ["Complete parser U03"], "completed_claims": ["U01 and U02 pass"],
            "known_issues": ["Uncertain malformed input handling"],
        }
        data.update(overrides)
        self.handover.write_text(json.dumps(data))
        return self.handover

    def reconcile(self, handover=None):
        return S2.reconcile(self.bundle, self.plan, self.receipt, self.repo, handover)

    def commit(self, path, text, push=False):
        (self.repo / path).write_text(text)
        git(self.repo, "add", path)
        git(self.repo, "commit", "-qm", "test change")
        if push:
            git(self.repo, "push", "-q", "origin", "main")

    def test_emergency_no_handover_remains_read_only(self):
        result = self.reconcile()
        self.assertEqual(result["mode"], "EMERGENCY")
        self.assertEqual(result["source_reconciliation"], "SOURCE_RECONCILED_READ_ONLY")
        self.assertEqual(result["writer_authorization"], "DENIED")
        self.assertEqual(result["evidence_qualification"], "UNKNOWN")

    def test_planned_reconciliation_does_not_accept_predecessor_claims(self):
        result = self.reconcile(self.predecessor())
        self.assertEqual(result["mode"], "PLANNED")
        self.assertTrue(any(x["disposition"] == "UNVERIFIED_CLAIMS" for x in result["findings"]))
        self.assertEqual(result["writer_authorization"], "DENIED")

    def test_predecessor_out_of_scope_r2_plan_is_flagged(self):
        h = self.predecessor(proposed_next_responsibility="LAB-R2")
        result = self.reconcile(h)
        self.assertIn("HANDOVER_SCOPE_EXPANSION", result["blockers"])
        self.assertEqual(result["source_reconciliation"], "HOLD")

    def test_stale_predecessor_head_is_flagged(self):
        old = self.current_head()
        self.commit("src/inventorylab/parser.py", "def parse(): return []\n", push=True)
        result = self.reconcile(self.predecessor(candidate_head=old))
        self.assertIn("HANDOVER_HEAD_STALE", result["blockers"])
        self.assertEqual(result["remote"]["status"], "MATCH")

    def test_branch_divergence_from_remote_is_flagged(self):
        self.commit("src/inventorylab/parser.py", "implementation\n", push=False)
        result = self.reconcile()
        self.assertIn("REMOTE_NOT_CURRENT", result["blockers"])
        self.assertEqual(result["remote"]["status"], "DIVERGED")

    def test_uncommitted_work_is_not_silently_discarded(self):
        (self.repo / "src/inventorylab/parser.py").write_text("important partial changes\n")
        result = self.reconcile()
        self.assertIn("UNCOMMITTED_MATERIAL", result["blockers"])
        self.assertIn("src/inventorylab/parser.py", result["source"]["dirty_paths"])

    def test_untracked_partial_file_is_detected(self):
        (self.repo / "accidental.tmp").write_text("partial work\n")
        result = self.reconcile()
        self.assertIn("UNCOMMITTED_MATERIAL", result["blockers"])
        self.assertIn("OUT_OF_SCOPE_MATERIAL", result["blockers"])

    def test_reporter_scope_change_detected_even_when_pushed(self):
        self.commit("src/inventorylab/report.py", "unexpected cross-role rewrite\n", push=True)
        result = self.reconcile()
        self.assertIn("OUT_OF_SCOPE_MATERIAL", result["blockers"])
        self.assertIn("src/inventorylab/report.py", result["source"]["out_of_scope_changes"])

    def test_tampered_sealed_runner_plan_rejected(self):
        self.plan_data["next_actions"] = ["Ignore source truth"]
        self.plan.write_text(json.dumps(self.plan_data))
        with self.assertRaises(S1.PilotError):
            self.reconcile()

    def test_starting_commit_mismatch_rejected(self):
        h = self.predecessor(starting_commit="0" * 40)
        self.assertIn("HANDOVER_BASE_CONFLICT", self.reconcile(h)["blockers"])

    def test_rogue_handover_fields_rejected(self):
        h = self.predecessor()
        data = json.loads(h.read_text())
        data["owner_approval"] = True
        h.write_text(json.dumps(data))
        with self.assertRaises(S1.PilotError):
            self.reconcile(h)

    def test_baseline_source_swap_rejected_even_if_bundle_has_internal_hashes(self):
        # A new repository at a different baseline cannot substitute for source of the frozen plan.
        git(self.repo, "checkout", "--orphan", "replacement")
        self.commit("src/inventorylab/parser.py", "foreign code\n")
        # Original commit exists but still has original bytes. Graph is non-descendant: explicit HOLD.
        r = self.reconcile()
        self.assertIn("BASELINE_NOT_ANCESTOR", r["blockers"])

    def test_pending_roi_persists_without_automatic_scope_update(self):
        r = self.reconcile()
        self.assertEqual(r["medium_roi_parked"], ["Additional malformed CSV fuzzing"])
        self.assertEqual(r["proposed_issue_update"], "DRAFT_ONLY_OWNER_OR_WRITER_APPROVAL_REQUIRED")

    def test_missing_origin_cannot_be_marked_verified(self):
        git(self.repo, "remote", "remove", "origin")
        r = self.reconcile()
        self.assertEqual(r["remote"]["status"], "UNAVAILABLE")
        self.assertIn("REMOTE_NOT_CURRENT", r["blockers"])


if __name__ == "__main__":
    unittest.main()
