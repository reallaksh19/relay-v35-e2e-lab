#!/usr/bin/env python3
"""WP0 author-side native-module falsifiers. Synthetic facts; no provider writes."""
import importlib.util
import os
from pathlib import Path
import re
import unittest

ROOT = Path(os.environ["COMMON_CHECKOUT"]).resolve()
V32 = ROOT / "skills/engineering-pr-delivery-v3.2/scripts"
RELAY = ROOT / "skills/engineering-relay-v1"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CONT = load("continuity_wp0", V32 / "continuity_projection.py")
DELP = load("delp_wp0", V32 / "delp_projection_v32.py")
A, B = "a" * 40, "b" * 40
REF = "Common#592#issuecomment-1"


def graph():
    # Source-compatible specimen adapted from real test_delp_projection_v32.py::graph.
    return {
        "schema": DELP.GRAPH_SCHEMA,
        "programme": {"id": "WP0-SYNTHETIC", "root": "Common#527"},
        "nodes": [
            {"ref": "Common#527", "kind": "ROOT"},
            {"ref": "Common#588", "kind": "INTERMEDIATE", "parent": "Common#527", "weight": 3},
            {"ref": "Common#610", "kind": "INTERMEDIATE", "parent": "Common#527", "weight": 1},
            {"ref": "Common#592", "kind": "LEAF", "parent": "Common#588", "weight": 3,
             "responsibility_id": "WP0-R", "primary_pr": "Common#593",
             "units": [{"id": "U01", "weight": 100}]},
            {"ref": "Common#594", "kind": "LEAF", "parent": "Common#588", "weight": 1,
             "primary_pr": "Common#595", "units": [{"id": "V1", "weight": 100}]},
            {"ref": "Common#612", "kind": "LEAF", "parent": "Common#610", "weight": 1,
             "primary_pr": "Common#613", "units": [{"id": "W1", "weight": 100}]},
        ],
    }


def facts(result="VERIFIED", candidate=A):
    return [{
        "source": "WP0-SYNTHETIC-FACT", "order": 1,
        "facts": {
            "schema": DELP.FACTS_SCHEMA,
            "responsibility": {"issue": "Common#592"},
            "material": {"pr": "Common#593", "candidate_sha": candidate},
            "units": [{"id": "U01", "state": "COMPLETE",
                       "result": result, "evidence_refs": [REF]}],
        },
    }]


def proj(result="VERIFIED", observed=A):
    return DELP.project(graph(), facts(result), {
        "Common#592": {"candidate_sha": observed},
    })["nodes"]["Common#592"]


class NativeWP0Falsifiers(unittest.TestCase):
    def test_n3_failed_claim_continuity_false_positive_vs_delp(self):
        legacy = CONT.progress([{
            "id": "U01", "weight": 100, "complete": True,
            "result": "FAILED", "evidence_refs": [REF],
            "evidence_candidate": A,
        }], derived=True, material_head=A)
        node = proj("FAILED")
        self.assertEqual((100, 100), (legacy["progress_percent"], legacy["evidence_percent"]))
        self.assertEqual((100, 0), (node["progress"]["P"], node["progress"]["E"]))
        self.assertEqual("RESULT_NOT_ACCEPTED(FAILED)", node["evidence"]["gaps"][0]["reason"])
        print("N3 EXPECTED_DIVERGENCE continuity P100/E100; DELP P100/E0 (FAILED)")

    def test_n3_verified_positive_control(self):
        node = proj("VERIFIED")
        self.assertEqual((100, 100), (node["progress"]["P"], node["progress"]["E"]))
        print("N3 POSITIVE_CONTROL DELP P100/E100 (VERIFIED)")

    def test_n3_stale_head_negative_control(self):
        node = proj("VERIFIED", observed=B)
        self.assertEqual((100, 0), (node["progress"]["P"], node["progress"]["E"]))
        self.assertEqual("CANDIDATE_MISMATCH", node["evidence"]["gaps"][0]["reason"])
        print("N3 STALE_HEAD_CONTROL DELP P100/E0")

    def test_n2_native_relay_import_closure_has_no_delp_call(self):
        start = RELAY / "full-chain-rehearsal-v1.mjs"
        queue, seen = [start], set()
        while queue:
            f = queue.pop()
            if f in seen:
                continue
            self.assertTrue(f.is_file(), str(f))
            seen.add(f)
            source = f.read_text(encoding="utf-8")
            self.assertNotRegex(
                source, r"delp_projection|DELP\.project\(|delp\.project\(|child_process|spawnSync|execFile",
                f"unexpected DELP call/bridge in {f.name}")
            for dep in re.findall(r"""(?:^|\n)\s*import\s+(?:[^'\n]*?\s+from\s+)?['"]\./([^'"]+)['"]""", source):
                queue.append(f.parent / dep)
        self.assertEqual(13, len(seen), "inspect closure growth before interpreting result")
        print("N2 STATIC_IMPORT_NEGATIVE 13 real ESM files; no programme DELP call located")

    def test_n1_c6_positive_source_guard(self):
        source = (V32 / "handover_context.py").read_text(encoding="utf-8")
        self.assertIn("delp.project(graph, facts, observed_after)", source)
        self.assertIn("delp.source_bound_responsibility_core(graph, projection, leaf_ref)", source)
        print("N1 SOURCE_GUARD native V3.2 C6→DELP invocation present")


if __name__ == "__main__":
    unittest.main(verbosity=2)
