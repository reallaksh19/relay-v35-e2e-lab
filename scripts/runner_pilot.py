#!/usr/bin/env python3
"""Runner Stage-1 preparation pilot. Read-only evidence, NOT a custody or DELP authority.

Run successors in a separate filesystem/network/credential sandbox; packaging alone
is not runtime isolation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SCHEMA = "RUNNER_PREPARATION_V1"
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,99}$")
STAGE1_PATHS = (
    "docs/owner-intent.md",
    "fixtures/valid.csv",
    "src/inventorylab/parser.py",
    "tests/test_inventory_parser.py",
)
BRIEF_KEYS = frozenset({"schema", "responsibility", "what", "why", "claims",
                        "pending", "known_issues", "parked", "source_refs"})
PLAN_KEYS = frozenset({"schema", "responsibility", "source_bundle_digest", "purpose",
                       "next_actions", "unknowns", "stage2_questions", "parked_medium_roi"})
RISK_SIGNALS = frozenset({"NONE", "CONTEXT_LOSS", "TOOL_FAILURE", "COMPACTION",
                          "EXPLICIT_OWNER_REQUEST"})


class PilotError(ValueError):
    pass


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def require_id(value: str, field: str) -> None:
    if not ID_RE.fullmatch(value):
        raise PilotError(f"invalid {field}")


def load_object(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise PilotError("expected JSON object")
    return data


def exclusive_json(path: Path, obj: dict) -> None:
    """Single-host idempotency, NOT a distributed lease, authentication or approval."""
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as fh:
        fh.write(canonical(obj))
        fh.flush()
        os.fsync(fh.fileno())


def trigger(epoch: str, responsibility: str, state_dir: Path,
            used: int | None, budget: int | None, risk: str = "NONE",
            threshold: int = 70) -> dict:
    require_id(epoch, "epoch")
    require_id(responsibility, "responsibility")
    if risk not in RISK_SIGNALS or not 0 < threshold < 100:
        raise PilotError("invalid risk or threshold")
    if (used is None) != (budget is None):
        raise PilotError("used and budget must both be present or both absent")
    if used is not None and (used < 0 or budget <= 0 or used > budget):
        raise PilotError("invalid context telemetry")
    consumed = None if used is None else round(100 * used / budget, 2)
    requested = risk != "NONE" or (consumed is not None and consumed >= threshold)
    if not requested:
        return {"schema": SCHEMA, "event": "PRIMARY_CONTINUES", "consumed_percent": consumed,
                "telemetry": "UNKNOWN" if consumed is None else "CALLER_PROVIDED", "risk": risk}
    state_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
    path = state_dir / f"{epoch}.{responsibility}.runner-request.json"
    record = {"schema": SCHEMA, "event": "TIME_FOR_RUNNER_REQUESTED",
              "declaration": "Time for runner", "epoch": epoch,
              "responsibility": responsibility, "consumed_percent": consumed,
              "telemetry": "UNKNOWN" if consumed is None else "CALLER_PROVIDED",
              "risk": risk, "threshold_percent": threshold,
              "execution_authority": "PRIMARY_RETAINED",
              "runner_authority": "READ_ONLY"}
    try:
        exclusive_json(path, record)
    except FileExistsError:
        prior = load_object(path)
        if (prior.get("epoch") != epoch or prior.get("responsibility") != responsibility
                or prior.get("event") != "TIME_FOR_RUNNER_REQUESTED"):
            raise PilotError("runner request identity conflict")
        return prior
    return record


def validate_brief(brief: dict) -> None:
    if (set(brief) != BRIEF_KEYS or brief.get("schema") != "RUNNER_WHAT_WHY_V1"
            or brief.get("responsibility") != "LAB-R1"):
        raise PilotError("brief schema, identity or fields invalid")
    for key in ("what", "why"):
        if not isinstance(brief[key], str) or not brief[key].strip() or len(brief[key]) > 4000:
            raise PilotError(f"invalid {key}")
    for key in ("claims", "pending", "known_issues", "parked", "source_refs"):
        values = brief[key]
        if (not isinstance(values, list) or len(values) > 40
                or not all(isinstance(v, str) and 0 < len(v) < 1000 for v in values)):
            raise PilotError(f"invalid {key}")
    if any(ref not in STAGE1_PATHS for ref in brief["source_refs"]):
        raise PilotError("brief source refs must be pinned Stage-1 paths")


def git_blob(repo: Path, commit: str, path: str) -> bytes:
    result = subprocess.run(["git", "-C", str(repo), "show", f"{commit}:{path}"],
                            capture_output=True, check=False)
    if result.returncode:
        raise PilotError(f"missing pinned source {path}: {result.stderr.decode(errors='replace')[:160]}")
    return result.stdout


def prepare(repo: Path, commit: str, dest: Path, brief_path: Path) -> dict:
    if not SHA_RE.fullmatch(commit):
        raise PilotError("source commit must be a full 40-digit SHA")
    repo, dest = repo.resolve(), dest.resolve()
    if dest == repo or repo in dest.parents:
        raise PilotError("Stage 1 bundle must be outside implementation checkout")
    if dest.exists():
        raise PilotError("Stage 1 destination already exists")
    brief = load_object(brief_path)
    validate_brief(brief)
    check = subprocess.run(["git", "-C", str(repo), "cat-file", "-t", commit],
                           capture_output=True, text=True, check=False)
    if check.returncode or check.stdout.strip() != "commit":
        raise PilotError("unknown starting commit")
    # Always fetch immutable original commit. Never read the current worktree.
    source = {p: git_blob(repo, commit, p) for p in STAGE1_PATHS}
    parent = dest.parent
    parent.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix=".runner-stage1-", dir=parent))
    try:
        files = {}
        for rel, raw in source.items():
            output = tmp / rel
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(raw)
            os.chmod(output, 0o600)
            files[rel] = digest(raw)
        brief_bytes = canonical(brief)
        (tmp / "runner_brief.json").write_bytes(brief_bytes)
        os.chmod(tmp / "runner_brief.json", 0o600)
        files["runner_brief.json"] = digest(brief_bytes)
        manifest = {"schema": SCHEMA, "mode": "STAGE1_ALLOWLIST_ONLY",
                    "responsibility": "LAB-R1", "source_commit": commit,
                    "source_status": "SYNTHETIC_LAB_ONLY", "files": files,
                    "access_control": "EXTERNAL_SANDBOX_REQUIRED",
                    "authority": "READ_ONLY_NO_PROVIDER_AUTHORITY"}
        (tmp / "runner_manifest.json").write_bytes(canonical(manifest))
        os.chmod(tmp / "runner_manifest.json", 0o600)
        os.rename(tmp, dest)
        return manifest
    finally:
        if tmp.exists():
            shutil.rmtree(tmp)


def verify_bundle(bundle: Path) -> dict:
    manifest = load_object(bundle / "runner_manifest.json")
    if (manifest.get("schema") != SCHEMA or manifest.get("mode") != "STAGE1_ALLOWLIST_ONLY"
            or manifest.get("authority") != "READ_ONLY_NO_PROVIDER_AUTHORITY"
            or manifest.get("responsibility") != "LAB-R1"
            or not SHA_RE.fullmatch(str(manifest.get("source_commit", "")))):
        raise PilotError("invalid manifest")
    expected = set(STAGE1_PATHS) | {"runner_brief.json"}
    if set(manifest.get("files", {})) != expected:
        raise PilotError("unexpected file declarations")
    actual = set()
    for entry in bundle.rglob("*"):
        if entry.is_symlink():
            raise PilotError("symlink in bundle")
        if entry.is_file():
            actual.add(entry.relative_to(bundle).as_posix())
    if actual != expected | {"runner_manifest.json"}:
        raise PilotError("unexpected or missing bundle contents")
    for rel, sha in manifest["files"].items():
        if digest((bundle / rel).read_bytes()) != sha:
            raise PilotError(f"source bundle changed: {rel}")
    validate_brief(load_object(bundle / "runner_brief.json"))
    return manifest


def freeze(bundle: Path, plan_path: Path, record_path: Path) -> dict:
    manifest = verify_bundle(bundle)
    plan = load_object(plan_path)
    if set(plan) != PLAN_KEYS or plan.get("schema") != "RUNNER_RECONSTRUCTION_V1":
        raise PilotError("invalid reconstruction plan structure")
    if plan.get("responsibility") != "LAB-R1":
        raise PilotError("plan identity mismatch")
    bundle_digest = digest(canonical(manifest))
    if plan.get("source_bundle_digest") != bundle_digest:
        raise PilotError("plan was not based on the current Stage 1 bundle")
    if not isinstance(plan.get("purpose"), str) or not plan["purpose"].strip():
        raise PilotError("missing independent purpose")
    for k in ("next_actions", "unknowns", "stage2_questions", "parked_medium_roi"):
        v = plan[k]
        if not isinstance(v, list) or not all(isinstance(s, str) and s.strip() for s in v):
            raise PilotError(f"invalid plan field: {k}")
    if not plan["next_actions"] or len(plan["stage2_questions"]) != 3:
        raise PilotError("a next action and exactly three Stage 2 questions are required")
    record = {"schema": "RUNNER_RECONSTRUCTION_FREEZE_V1", "responsibility": "LAB-R1",
              "source_bundle_digest": bundle_digest, "plan_digest": digest(canonical(plan)),
              "status": "SEALED_READ_ONLY", "authority": "NONE",
              "caveat": "Local file integrity only; host signing and isolation must be externally enforced"}
    try:
        exclusive_json(record_path, record)
    except FileExistsError:
        if load_object(record_path) != record:
            raise PilotError("plan freeze is immutable")
    return record


def verify_freeze(bundle: Path, plan_path: Path, record_path: Path) -> dict:
    record = load_object(record_path)
    if record.get("schema") != "RUNNER_RECONSTRUCTION_FREEZE_V1" or record.get("authority") != "NONE":
        raise PilotError("invalid freeze receipt")
    if record.get("source_bundle_digest") != digest(canonical(verify_bundle(bundle))):
        raise PilotError("bundle digest changed since freeze")
    if record.get("plan_digest") != digest(canonical(load_object(plan_path))):
        raise PilotError("plan changed after freeze")
    return record


def main() -> None:
    ap = argparse.ArgumentParser(description="Read-only V3.5 Runner Stage 1 pilot; no GitHub writes")
    sub = ap.add_subparsers(dest="command", required=True)
    t = sub.add_parser("trigger")
    t.add_argument("--epoch", required=True)
    t.add_argument("--responsibility", required=True)
    t.add_argument("--state-dir", type=Path, required=True)
    t.add_argument("--used", type=int)
    t.add_argument("--budget", type=int)
    t.add_argument("--risk", choices=sorted(RISK_SIGNALS), default="NONE")
    t.add_argument("--threshold", type=int, default=70)
    p = sub.add_parser("prepare")
    p.add_argument("--repo", type=Path, required=True)
    p.add_argument("--commit", required=True)
    p.add_argument("--dest", type=Path, required=True)
    p.add_argument("--brief", type=Path, required=True)
    f = sub.add_parser("freeze")
    f.add_argument("--bundle", type=Path, required=True)
    f.add_argument("--plan", type=Path, required=True)
    f.add_argument("--receipt", type=Path, required=True)
    v = sub.add_parser("verify")
    v.add_argument("--bundle", type=Path, required=True)
    v.add_argument("--plan", type=Path, required=True)
    v.add_argument("--receipt", type=Path, required=True)
    args = ap.parse_args()
    try:
        if args.command == "trigger":
            out = trigger(args.epoch, args.responsibility, args.state_dir, args.used, args.budget, args.risk, args.threshold)
        elif args.command == "prepare":
            out = prepare(args.repo, args.commit, args.dest, args.brief)
        elif args.command == "freeze":
            out = freeze(args.bundle, args.plan, args.receipt)
        else:
            out = verify_freeze(args.bundle, args.plan, args.receipt)
        print(json.dumps(out, sort_keys=True, indent=2))
    except (PilotError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"RUNNER_PILOT_DENIED: {exc}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
