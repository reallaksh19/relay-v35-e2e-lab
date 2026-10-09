#!/usr/bin/env python3
"""Render a *draft* CHECKPOINT_FACTS_V1 body without any agent-authored P/E.

Publishing still requires real GitHub evidence and DELP validation. This is not
an evidence oracle and does not confer provider/reviewer/Owner authority.
"""
from __future__ import annotations
import argparse
import re
import yaml


def main() -> None:
    p = argparse.ArgumentParser(description="Prepare an unposted lab checkpoint fact block")
    p.add_argument("--repository", default="reallaksh19/relay-v35-e2e-lab")
    p.add_argument("--issue", required=True, type=int)
    p.add_argument("--pr", required=True, type=int)
    p.add_argument("--head", required=True)
    p.add_argument("--unit", required=True, choices=["U01", "U02", "U03"])
    p.add_argument("--result", required=True, choices=["VERIFIED", "FAILED", "NOT_RUN", "PENDING"])
    p.add_argument("--state", required=True, choices=["COMPLETE", "IN_PROGRESS", "NOT_STARTED"])
    p.add_argument("--evidence-ref", required=True)
    a = p.parse_args()
    if not re.fullmatch('[0-9a-f]{40}', a.head):
        p.error('--head must be an exact 40-char lowercase git SHA')
    if a.issue <= 0 or a.pr <= 0:
        p.error('positive issue and PR numbers required')
    repo = a.repository.split('/')[-1]
    facts = {"CHECKPOINT_FACTS_V1": {
      "responsibility": {"issue": f"{repo}#{a.issue}"},
      "material": {"pr": f"{repo}#{a.pr}", "candidate_sha": a.head},
      "units": [{"id": a.unit, "state": a.state,
                 "result": a.result, "evidence_refs": [a.evidence_ref]}],
      "activity": "ACTIVE", "blocker": "NONE", "owner_action": "NONE",
    }}
    print("TASK_EVIDENCE — PROPOSED LAB CHECKPOINT (verify exact head and CI first)\n")
    print("```yaml\n" + yaml.safe_dump(facts, sort_keys=False).rstrip() + "\n```")


if __name__ == '__main__':
    main()
