#!/usr/bin/env python3
"""RNR-04: source-first runner reconciliation. Read-only; NEVER execution admission.

A frozen Stage-1 plan is *hypothesis*, a predecessor handover is *claim*,
and Git/remote source observations are separate. Neither may mint evidence,
Owner permission, reviewer approval, a DELP score, or a writer epoch.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import runner_pilot as S1

SCHEMA = "RUNNER_RECONCILIATION_V1"
ALLOWED_RESPONSIBILITY = "LAB-R1"
ALLOWED_SOURCE_CHANGES = frozenset(("src/inventorylab/parser.py", "tests/test_inventory_parser.py"))
HANDOVER_FIELDS = frozenset(("schema", "responsibility", "starting_commit", "candidate_head",
                             "branch", "proposed_next_responsibility", "proposed_plan",
                             "completed_claims", "known_issues"))
SHA = re.compile(r"^[0-9a-f]{40}$")


def git(repo: Path, *args: str, timeout: int = 12, check: bool = True) -> bytes:
    result = subprocess.run(["git", "-C", str(repo), *args], stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, check=False, timeout=timeout)
    if check and result.returncode:
        raise S1.PilotError("git observation failed: " + " ".join(args[:2]) +
                            " (" + str(result.returncode) + ")")
    return result.stdout


def observed_git(repo: Path, baseline: str) -> dict[str, Any]:
    root = Path(git(repo, "rev-parse", "--show-toplevel").decode().strip()).resolve()
    if root != repo.resolve():
        raise S1.PilotError("source root must be the exact Git checkout")
    if not SHA.fullmatch(baseline):
        raise S1.PilotError("invalid baseline")
    if git(repo, "cat-file", "-t", baseline).strip() != b"commit":
        raise S1.PilotError("baseline is not a commit")
    current = git(repo, "rev-parse", "--verify", "HEAD").decode().strip()
    branch = git(repo, "symbolic-ref", "--quiet", "--short", "HEAD", check=False).decode().strip()
    ancestor = subprocess.run(["git", "-C", str(repo), "merge-base", "--is-ancestor", baseline, current],
                             capture_output=True, timeout=12).returncode == 0
    # Compare entire tracked change set since original baseline, including staged / unstaged.
    between = git(repo, "diff", "--name-only", "-z", baseline, current).decode().split("\0")
    staged = git(repo, "diff", "--cached", "--name-only", "-z").decode().split("\0")
    unstaged = git(repo, "diff", "--name-only", "-z").decode().split("\0")
    untracked = git(repo, "ls-files", "--others", "--exclude-standard", "-z").decode().split("\0")
    changed = sorted({p for p in between + staged + unstaged + untracked if p})
    dirty = sorted({p for p in staged + unstaged + untracked if p})
    # Empty branch means detached HEAD and cannot be an authorized writer.
    return {"baseline": baseline, "candidate_head": current, "branch": branch,
            "base_is_ancestor": ancestor, "changed_paths": changed, "dirty_paths": dirty,
            "out_of_scope_changes": sorted(set(changed) - ALLOWED_SOURCE_CHANGES)}


def observed_remote(repo: Path, branch: str, candidate: str) -> dict[str, Any]:
    if not branch or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9./_-]*", branch):
        return {"status": "UNAVAILABLE", "reason": "DETACHED_OR_INVALID_BRANCH"}
    try:
        # Do not accept caller-authored GitHub HEAD declarations as remote verification.
        result = subprocess.run(["git", "-C", str(repo), "ls-remote", "--exit-code",
                                 "origin", "refs/heads/" + branch], capture_output=True, timeout=12)
    except (OSError, subprocess.TimeoutExpired):
        return {"status": "UNAVAILABLE", "reason": "REMOTE_GET_FAILED"}
    if result.returncode:
        return {"status": "UNAVAILABLE", "reason": "REMOTE_GET_FAILED"}
    lines = result.stdout.decode(errors="replace").splitlines()
    if len(lines) != 1 or "\t" not in lines[0]:
        return {"status": "UNAVAILABLE", "reason": "REMOTE_REFERENCE_AMBIGUOUS"}
    ref_head, ref_name = lines[0].split("\t", 1)
    if not SHA.fullmatch(ref_head) or ref_name != "refs/heads/" + branch:
        return {"status": "UNAVAILABLE", "reason": "REMOTE_REFERENCE_INVALID"}
    return {"status": "MATCH" if ref_head == candidate else "DIVERGED",
            "remote_head": ref_head, "observed_ref": ref_name}


def parse_handover(path: Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    h = S1.load_object(path)
    if set(h) != HANDOVER_FIELDS or h.get("schema") != "RUNNER_PRIMARY_HANDOVER_V1":
        raise S1.PilotError("invalid primary handover structure")
    if h["responsibility"] != ALLOWED_RESPONSIBILITY or not SHA.fullmatch(str(h["starting_commit"])) \
            or not SHA.fullmatch(str(h["candidate_head"])):
        raise S1.PilotError("handover identity/commit invalid")
    for key in ("proposed_plan", "completed_claims", "known_issues"):
        v = h[key]
        if not isinstance(v, list) or len(v) > 80 or not all(isinstance(x, str) and 0 < len(x) <= 1000 for x in v):
            raise S1.PilotError("handover contains malformed " + key)
    for key in ("branch", "proposed_next_responsibility"):
        if not isinstance(h[key], str) or not h[key].strip() or len(h[key]) > 120:
            raise S1.PilotError("handover contains malformed " + key)
    return h


def reconcile(bundle: Path, plan_path: Path, receipt_path: Path, repo: Path,
              handover_path: Path | None = None) -> dict[str, Any]:
    # Freeze integrity is checked *before* revealing current state or Agent A's plan.
    freeze = S1.verify_freeze(bundle, plan_path, receipt_path)
    manifest = S1.verify_bundle(bundle)
    plan = S1.load_object(plan_path)
    if plan.get("schema") != "RUNNER_RECONSTRUCTION_V1" or \
            freeze.get("status") != "SEALED_READ_ONLY" or \
            manifest["responsibility"] != ALLOWED_RESPONSIBILITY:
        raise S1.PilotError("Stage-1 plan is not independently sealed")
    base = manifest["source_commit"]
    # Important cross-check: the bundled WHAT/WHY source files actually match this Git object.
    for path in S1.STAGE1_PATHS:
        if S1.digest(S1.git_blob(repo, base, path)) != manifest["files"][path]:
            raise S1.PilotError("Stage-1 source bundle is not from this repository baseline")
    observed = observed_git(repo, base)
    remote = observed_remote(repo, observed["branch"], observed["candidate_head"])
    handover = parse_handover(handover_path)
    blockers: list[str] = []
    findings: list[dict[str, str]] = []
    def flag(code: str, finding: str, disposition: str = "RECONCILE") -> None:
        blockers.append(code)
        findings.append({"finding": finding, "disposition": disposition})
    if not observed["base_is_ancestor"]:
        flag("BASELINE_NOT_ANCESTOR", "Working branch is not descended from the frozen starting commit")
    if observed["dirty_paths"]:
        flag("UNCOMMITTED_MATERIAL", "Staged, unstaged or untracked material requires explicit recovery")
    if observed["out_of_scope_changes"]:
        flag("OUT_OF_SCOPE_MATERIAL", "Worktree contains changes beyond the LAB-R1 source scope")
    if remote["status"] != "MATCH":
        flag("REMOTE_NOT_CURRENT", "Remote branch cannot be verified at the local candidate")
    if handover is None:
        findings.append({"finding": "Agent A unavailable: emergency takeover without final handover",
                         "disposition": "SOURCE_FIRST_RECOVERY"})
    else:
        if handover["starting_commit"] != base:
            flag("HANDOVER_BASE_CONFLICT", "Predecessor starting commit contradicts Stage-1 baseline")
        if handover["candidate_head"] != observed["candidate_head"]:
            flag("HANDOVER_HEAD_STALE", "Predecessor candidate does not match observed Git HEAD")
        if handover["branch"] != observed["branch"]:
            flag("HANDOVER_BRANCH_STALE", "Predecessor branch contradicts observed Git branch")
        if handover["proposed_next_responsibility"] != ALLOWED_RESPONSIBILITY:
            flag("HANDOVER_SCOPE_EXPANSION", "Predecessor proposes a different responsibility",
                 "OWNER_DECISION_REQUIRED")
        if handover["proposed_plan"] != plan["next_actions"]:
            findings.append({"finding": "Agent A proposed plan differs from frozen Runner B plan",
                             "disposition": "RECONCILE_INDEPENDENTLY"})
        findings.append({"finding": "Agent A completion claims require independent tests and exact-head evidence",
                         "disposition": "UNVERIFIED_CLAIMS"})
    # This stage NEVER claims acceptance, approved plan or execution permission.
    return {"schema": SCHEMA, "responsibility": ALLOWED_RESPONSIBILITY,
            "mode": "PLANNED" if handover is not None else "EMERGENCY",
            "frozen_plan_digest": freeze["plan_digest"], "frozen_bundle_digest": freeze["source_bundle_digest"],
            "source": observed, "remote": remote, "blockers": sorted(set(blockers)),
            "findings": findings, "independent_next_actions": plan["next_actions"],
            "medium_roi_parked": plan["parked_medium_roi"],
            "proposed_issue_update": "DRAFT_ONLY_OWNER_OR_WRITER_APPROVAL_REQUIRED",
            "source_reconciliation": "HOLD" if blockers else "SOURCE_RECONCILED_READ_ONLY",
            "evidence_qualification": "UNKNOWN", "reviewer_verdict": "UNKNOWN",
            "writer_authorization": "DENIED", "custody_transfer": "NOT_EXECUTED"}


def main() -> None:
    ap = argparse.ArgumentParser(description="LAB RNR-04 Stage 2; source-only, no GitHub writes")
    ap.add_argument("--bundle", type=Path, required=True)
    ap.add_argument("--plan", type=Path, required=True)
    ap.add_argument("--receipt", type=Path, required=True)
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--handover", type=Path, help="optional; absent means emergency takeover")
    a = ap.parse_args()
    try:
        print(json.dumps(reconcile(a.bundle, a.plan, a.receipt, a.repo, a.handover), indent=2, sort_keys=True))
    except (S1.PilotError, OSError, ValueError, subprocess.TimeoutExpired) as exc:
        print("RUNNER_STAGE2_DENIED: " + str(exc), file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
