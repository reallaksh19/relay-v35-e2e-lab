import importlib.util
import unittest
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "scripts/generate_graph.py"
S = importlib.util.spec_from_file_location("lab_graph", P)
M = importlib.util.module_from_spec(S)
S.loader.exec_module(M)


class GeneratedGraphShape(unittest.TestCase):
    def test_real_issue_refs_and_weights(self):
        g = M.make_graph("reallaksh19/relay-v35-e2e-lab", 11, 12, 13)
        self.assertEqual([n["ref"] for n in g["nodes"]], [
            "relay-v35-e2e-lab#11", "relay-v35-e2e-lab#12", "relay-v35-e2e-lab#13"])
        self.assertEqual([u["weight"] for u in g["nodes"][1]["units"]], [35, 35, 30])
        self.assertEqual(g["nodes"][2]["depends_on"], ["relay-v35-e2e-lab#12"])
        self.assertEqual(g["programme"]["decomposition_policy"]["mode"], "ENFORCED")

    def test_reject_duplicate_issue_numbers(self):
        with self.assertRaises(ValueError):
            M.make_graph("reallaksh19/relay-v35-e2e-lab", 11, 12, 12)

    def test_reject_foreign_repo_or_bad_identity(self):
        for name in ("", "repo", "foo/bar/baz"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                M.make_graph(name, 11, 12, 13)
