#!/usr/bin/env python3
"""Generate a coordinator-owned V3.2 DELP graph from ACTUAL GitHub issue IDs.

This is a lab plan scaffold, not Owner authentication or source approval.
The canonical V3.2 delp_projection_v32.py must validate it separately.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
import yaml


def issue_number(value: int) -> int:
    if value < 1:
        raise ValueError("GitHub issue numbers must be positive")
    return value


def make_graph(repository: str, root: int, parser: int, report: int) -> dict:
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
        raise ValueError("repository must be OWNER/REPO")
    for issue in (root, parser, report):
        issue_number(issue)
    if len({root, parser, report}) != 3:
        raise ValueError("programme and child issues must be distinct")
    name = repository.split("/", 1)[1]
    ref = lambda issue: f"{name}#{issue}"

    def leaf(issue: int, responsibility: str, dependency: list[str], outcome: str,
             paths: list[str], specs: list[tuple[str, str]]) -> dict:
        return {
            "ref": ref(issue), "kind": "LEAF", "parent": ref(root), "weight": 1,
            "responsibility_id": responsibility, "depends_on": dependency,
            "outcome": outcome, "write_surface": paths,
            "size_budget": {"target_loc": 300, "hard_loc": 800,
                            "target_minutes": 15, "hard_minutes": 20},
            "units": [
                {"id": spec_id, "weight": weight,
                 "verify": verify, "outcome": verify}
                for (spec_id, verify), weight in zip(specs, (35, 35, 30))
            ],
        }

    return {
        "schema": "relay-v3.2-delp-execution-graph",
        "programme": {
            "id": "LAB-V35-R14-ONE-DELP-PROTO", "root": ref(root),
            "repository": repository, "total_weight": 10000,
            "decomposition_policy": {"mode": "ENFORCED"},
        },
        "nodes": [
            {"ref": ref(root), "kind": "ROOT"},
            leaf(parser, "LAB-R1-PARSER", [],
                 "Deterministic, strict CSV parser rejects invalid records.",
                 ["src/inventorylab/parser.py", "tests/test_inventory_parser.py"],
                 [("U01", "Valid rows parse with Decimal precision"),
                  ("U02", "Invalid and repeated SKUs fail closed"),
                  ("U03", "Exact-head parser unit tests pass after interruption recovery")]),
            leaf(report, "LAB-R2-REPORT", [ref(parser)],
                 "Deterministic SKU-sorted JSON report and CLI.",
                 ["src/inventorylab/report.py", "src/inventorylab/__main__.py",
                  "tests/test_inventory_report.py"],
                 [("U01", "Rows are sorted deterministically"),
                  ("U02", "Exact Decimal item and total values are preserved"),
                  ("U03", "Exact-head end-to-end CLI tests pass")]),
        ],
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Build a V3.2 DELP lab graph from real GitHub issues")
    ap.add_argument("--repository", required=True)
    ap.add_argument("--parent", type=int, required=True)
    ap.add_argument("--parser", type=int, required=True)
    ap.add_argument("--report", type=int, required=True)
    ap.add_argument("--output", type=Path, default=Path(".relay/graph.yaml"))
    args = ap.parse_args()
    graph = make_graph(args.repository, args.parent, args.parser, args.report)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(yaml.safe_dump(graph, sort_keys=False, allow_unicode=True), encoding="utf-8")
    print(json.dumps({"graph_path": str(args.output), "repository": args.repository,
                      "node_refs": [n["ref"] for n in graph["nodes"]]}))


if __name__ == "__main__":
    main()
