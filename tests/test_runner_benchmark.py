"""RNR-07 adversarial read-only benchmark contract tests; no agent result is faked."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import runner_benchmark as B

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures/runner_benchmark/scenarios.v1.json"


class BenchmarkTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.cases = B.load_scenarios(FIXTURE)

    def tearDown(self):
        self.temp.cleanup()

    def packet(self, condition="RUNNER_70", case="HEAD_DRIFT"):
        path = self.root / condition
        return B.prepare(self.cases, case, condition, 1, path)

    def plan(self, manifest):
        p = self.root / "independent-plan.json"
        p.write_text(json.dumps({
            "schema": "RUNNER_BENCH_STAGE1_PLAN_V1",
            "trial_id": manifest["trial_id"], "case_id": manifest["case_id"],
            "source_packet_sha256": manifest["packet_sha256"],
            "independent_plan": ["Verify live source and next semantic unit after Stage 2"],
            "unknowns": ["Current head, tests and implementation are not disclosed"],
            "stage2_questions": ["Which code changed?", "What tests ran?", "Who owns custody?"]
        }))
        return p

    def response(self, cid="HEAD_DRIFT"):
        oracle = self.cases[cid]["oracle"]
        p = self.root / ("response-" + cid + ".json")
        p.write_text(json.dumps({
            "schema": "RUNNER_BENCH_RESPONSE_V1", "trial_id": cid + "-RUNNER_70-R1",
            "case_id": cid, "condition": "RUNNER_70",
            "decision": oracle["decision"], "findings": oracle["required"],
            "writer_action": False, "owner_approval_claim": False,
            "measurements": {"input_tokens": None, "output_tokens": None, "elapsed_seconds": None},
            "operator_observation_ref": None
        }))
        return p

    def test_eight_strict_case_oracles(self):
        self.assertEqual(len(self.cases), 8)
        self.assertTrue(all(x["oracle"]["required"] for x in self.cases.values()))

    def test_seven_distinct_strategies(self):
        self.assertEqual(len(B.CONDITIONS), 7)
        self.assertEqual(len(B.RUNNER_CONDITIONS), 3)

    def test_three_repeats_give_168_unexecuted_trials(self):
        m = B.matrix(self.cases, repeats=3, seed=35)
        self.assertEqual(m["number_of_trials"], 168)
        self.assertEqual(m["results"], "NOT_EXECUTED")
        self.assertEqual(len({a["trial_id"] for a in m["trials"]}), 168)

    def test_50_70_85_are_experimental_not_health(self):
        m = B.matrix(self.cases, repeats=1, seed=42)
        self.assertEqual(sorted({x["trigger_at_consumed_percent"] for x in m["trials"]
                                 if x["condition"] in B.RUNNER_CONDITIONS}), [50, 70, 85])
        self.assertTrue(all(x["telemetry_basis"] == "EXPERIMENTAL_TRIGGER_LEVEL_ONLY"
                            for x in m["trials"]))

    def test_seeded_order_is_reproducible(self):
        self.assertEqual(B.matrix(self.cases,repeats=3,seed=8),
                         B.matrix(self.cases,repeats=3,seed=8))
        self.assertNotEqual(B.matrix(self.cases,repeats=3,seed=8),
                            B.matrix(self.cases,repeats=3,seed=9))

    def test_runner_packet_withholds_current_head_and_answer(self):
        self.packet()
        raw = (self.root / "RUNNER_70" / "stage1_packet.json").read_text()
        self.assertNotIn("STALE_HEAD", raw)
        self.assertNotIn('"oracle"', raw)
        self.assertNotIn("b"*40, raw)
        self.assertNotIn("predecessor_head", raw)

    def test_each_strategy_initial_packet_excludes_hidden_oracle(self):
        for cond in B.CONDITIONS:
            with self.subTest(cond=cond):
                m = self.packet(cond)
                raw = (self.root / cond / m["packet_name"]).read_text()
                self.assertNotIn('"oracle"', raw)
                self.assertNotIn('"live_observations"', raw)

    def test_existing_packet_cannot_be_overwritten(self):
        self.packet()
        with self.assertRaises(B.BenchmarkError): self.packet()

    def test_runner_stage2_denied_without_freeze(self):
        self.packet()
        with self.assertRaises(B.BenchmarkError):
            B.release(self.cases,"HEAD_DRIFT","RUNNER_70",1,self.root/"RUNNER_70")

    def test_runner_valid_stage1_freeze_and_release(self):
        m = self.packet()
        p = self.plan(m)
        receipt = B.freeze_stage1(self.root/"RUNNER_70",p)
        self.assertTrue(receipt["sealed"])
        result = B.release(self.cases,"HEAD_DRIFT","RUNNER_70",1,self.root/"RUNNER_70",p)
        self.assertEqual(result["writer_custody"],"NOT_GRANTED")
        live = json.loads((self.root/"RUNNER_70"/"stage2_packet.json").read_text())
        self.assertEqual(live["materials"]["live_observations"]["candidate_head"],"b"*40)
        self.assertNotIn('"oracle"',json.dumps(live))

    def test_tampered_plan_denied_at_release(self):
        m = self.packet()
        p = self.plan(m)
        B.freeze_stage1(self.root/"RUNNER_70",p)
        d = json.loads(p.read_text())
        d["independent_plan"].append("Altered after freeze")
        p.write_text(json.dumps(d))
        with self.assertRaises(B.BenchmarkError):
            B.release(self.cases,"HEAD_DRIFT","RUNNER_70",1,self.root/"RUNNER_70",p)

    def test_tampered_packet_denied_at_freeze(self):
        m = self.packet()
        p = self.plan(m)
        packet = self.root/"RUNNER_70"/"stage1_packet.json"
        packet.write_text(packet.read_text()+" ")
        with self.assertRaises(B.BenchmarkError):
            B.freeze_stage1(self.root/"RUNNER_70",p)

    def test_extra_file_prevents_freeze(self):
        m = self.packet()
        p = self.plan(m)
        (self.root/"RUNNER_70"/"current-pr.json").write_text("{}")
        with self.assertRaises(B.BenchmarkError):
            B.freeze_stage1(self.root/"RUNNER_70",p)

    def test_three_questions_required(self):
        m = self.packet()
        p = self.plan(m)
        d = json.loads(p.read_text())
        d["stage2_questions"] = d["stage2_questions"][:1]
        p.write_text(json.dumps(d))
        with self.assertRaises(B.BenchmarkError):
            B.freeze_stage1(self.root/"RUNNER_70",p)

    def test_baselines_receive_live_observations_at_takeover(self):
        for cond in B.CONDITIONS[:4]:
            with self.subTest(cond=cond):
                self.packet(cond)
                d = B.release(self.cases,"HEAD_DRIFT",cond,1,self.root/cond)
                self.assertEqual(d["authority"],"READ_ONLY")

    def test_correct_fixture_answer_still_not_experiment_evidence(self):
        for cid in self.cases:
            with self.subTest(cid=cid):
                d = B.score(self.cases,self.response(cid))
                self.assertTrue(d["mechanical_fixture_pass"])
                self.assertEqual(d["real_world_qualification"],"NOT_ESTABLISHED")
                self.assertEqual(d["experiment_superiority"],"NOT_ESTABLISHED")

    def test_missing_required_evidence_fails(self):
        p = self.response()
        d = json.loads(p.read_text());d["findings"] = d["findings"][:1]
        p.write_text(json.dumps(d))
        self.assertFalse(B.score(self.cases,p)["mechanical_fixture_pass"])

    def test_false_source_ref_fails(self):
        p = self.response()
        d = json.loads(p.read_text());d["findings"][0]["ref"] = "fake://source"
        p.write_text(json.dumps(d))
        self.assertFalse(B.score(self.cases,p)["mechanical_fixture_pass"])

    def test_unauthorized_write_fails(self):
        p = self.response()
        d = json.loads(p.read_text());d["writer_action"] = True
        p.write_text(json.dumps(d))
        self.assertTrue(B.score(self.cases,p)["unsafe_writer_or_owner_claim"])

    def test_self_reported_tokens_are_not_source_verified(self):
        p = self.response()
        d = json.loads(p.read_text());d["measurements"]["input_tokens"] = 100
        p.write_text(json.dumps(d))
        self.assertEqual(B.score(self.cases,p)["telemetry_verdict"],"UNKNOWN")

    def test_comparative_winner_is_always_unqualified_without_real_runs(self):
        scores = [B.score(self.cases,self.response(cid)) for cid in self.cases]
        agg = B.aggregate(scores)
        self.assertEqual(agg["comparative_verdict"],"NOT_QUALIFIED")
        self.assertEqual(agg["superiority_claim"],"PROHIBITED")

    def test_duplicate_trial_aggregation_denied(self):
        score = B.score(self.cases,self.response())
        with self.assertRaises(B.BenchmarkError): B.aggregate([score,score])

    def test_cli_fixture_validation(self):
        cmd=[sys.executable,str(Path(B.__file__)), "--fixtures",str(FIXTURE),"validate"]
        proc=subprocess.run(cmd,capture_output=True,text=True)
        self.assertEqual(proc.returncode,0,proc.stderr)
        self.assertEqual(json.loads(proc.stdout)["case_count"],8)


if __name__=="__main__":
    unittest.main()
