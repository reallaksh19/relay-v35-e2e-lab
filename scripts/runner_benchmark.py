#!/usr/bin/env python3
"""RNR-07: read-only continuity trial packet builder, blind freeze and mechanical oracle.

No model execution, owner authentication, browser or GitHub write, or winner claims.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import random
import re
import sys
from pathlib import Path

SCHEMA = "RUNNER_BENCH_SCENARIOS_V1"
CONDITIONS = ("COLD_GITHUB", "TERMINAL_HANDOVER", "DURABLE_CHECKPOINT",
              "EVENT_SOURCED", "RUNNER_50", "RUNNER_70", "RUNNER_85")
RUNNER_CONDITIONS = frozenset(CONDITIONS[-3:])
DECISIONS = frozenset(("RECONCILE", "REPAIR", "OWNER_DECISION_REQUIRED", "MATERIALIZE", "HOLD"))
SHA40 = re.compile(r"^[a-f0-9]{40}$")
CODE = re.compile(r"^[A-Z][A-Z0-9_]{2,80}$")
ID = re.compile(r"^[A-Z][A-Z0-9_]{2,80}$")
PACKET_KEYS = frozenset(("schema", "trial_id", "case_id", "condition", "phase",
                         "materials", "authority", "owner_source_grade"))
PLAN_KEYS = frozenset(("schema", "trial_id", "case_id", "source_packet_sha256",
                       "independent_plan", "unknowns", "stage2_questions"))
RESPONSE_KEYS = frozenset(("schema", "trial_id", "case_id", "condition",
                           "decision", "findings", "writer_action", "owner_approval_claim",
                           "measurements", "operator_observation_ref"))


class BenchmarkError(ValueError):
    pass


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")


def sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def read_json(path: Path) -> dict:
    result = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(result, dict):
        raise BenchmarkError("JSON object required")
    return result


def atomic_once(path: Path, value: dict) -> None:
    fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    with os.fdopen(fd, "wb") as fh:
        fh.write(canonical(value))
        fh.flush()
        os.fsync(fh.fileno())


def load_scenarios(path: Path) -> dict[str, dict]:
    root = read_json(path)
    if (set(root) != {"schema", "source_grade", "scenarios"} or root["schema"] != SCHEMA
            or root["source_grade"] != "SYNTHETIC_LAB_ONLY"
            or not isinstance(root["scenarios"], list) or len(root["scenarios"]) < 6):
        raise BenchmarkError("invalid synthetic fixture set")
    cases = {}
    for case in root["scenarios"]:
        if not isinstance(case, dict) or set(case) != {"id", "challenge", "original", "live", "oracle"}:
            raise BenchmarkError("invalid scenario")
        cid = case["id"]
        if not isinstance(cid, str) or not ID.fullmatch(cid) or cid in cases:
            raise BenchmarkError("duplicate/invalid case")
        if (not isinstance(case["challenge"], str) or not case["challenge"].strip()
                or not isinstance(case["original"], dict)
                or not SHA40.fullmatch(str(case["original"].get("starting_commit", "")))
                or not isinstance(case["original"].get("source_inputs"), list)
                or not isinstance(case["live"], dict) or not isinstance(case["live"].get("sources"), dict)):
            raise BenchmarkError("invalid original/live case")
        oracle = case["oracle"]
        if not isinstance(oracle, dict) or set(oracle) != {"decision", "required"} or oracle["decision"] not in DECISIONS:
            raise BenchmarkError("invalid oracle")
        req = oracle["required"]
        if not isinstance(req, list) or not req:
            raise BenchmarkError("missing required oracle findings")
        seen = set()
        source_refs = set(case["live"]["sources"].values())
        if len(source_refs) != len(case["live"]["sources"]):
            raise BenchmarkError("duplicated live source refs")
        for item in req:
            if (not isinstance(item, dict) or set(item) != {"code", "ref"}
                    or not isinstance(item["code"], str) or not CODE.fullmatch(item["code"])
                    or item["code"] in seen or item["ref"] not in source_refs):
                raise BenchmarkError("unverifiable oracle")
            seen.add(item["code"])
        cases[cid] = case
    return cases


def matrix(cases: dict[str, dict], *, repeats: int, seed: int) -> dict:
    if type(repeats) is not int or not 1 <= repeats <= 10 or type(seed) is not int:
        raise BenchmarkError("invalid repetitions")
    trials = []
    for rep in range(1, repeats + 1):
        for cid in sorted(cases):
            for cond in CONDITIONS:
                trials.append({"trial_id": f"{cid}-{cond}-R{rep}", "case_id": cid,
                               "condition": cond, "repetition": rep,
                               "trigger_at_consumed_percent": int(cond.rsplit("_", 1)[1]) if cond in RUNNER_CONDITIONS else None,
                               "telemetry_basis": "EXPERIMENTAL_TRIGGER_LEVEL_ONLY",
                               "execution_principal": "UNASSIGNED", "status": "NOT_RUN"})
    random.Random(seed).shuffle(trials)
    return {"schema": "RUNNER_BENCH_MATRIX_V1", "seed": seed,
            "repeats": repeats, "number_of_trials": len(trials),
            "lab_source_grade": "SYNTHETIC_LAB_ONLY",
            "results": "NOT_EXECUTED", "trials": trials}


def _case(cases: dict[str, dict], cid: str, condition: str) -> dict:
    if cid not in cases or condition not in CONDITIONS:
        raise BenchmarkError("invalid scenario/strategy")
    return cases[cid]


def _trial_id(cid: str, condition: str, repeat: int) -> str:
    if type(repeat) is not int or not 1 <= repeat <= 10:
        raise BenchmarkError("repeat outside bound")
    return f"{cid}-{condition}-R{repeat}"


def _audit_dir(folder: Path, allowed: set[str]) -> None:
    if not folder.is_dir() or folder.is_symlink():
        raise BenchmarkError("invalid trial directory")
    found = set()
    for entry in folder.iterdir():
        if entry.is_symlink() or not entry.is_file():
            raise BenchmarkError("extra directory/symlink")
        found.add(entry.name)
    if found != allowed:
        raise BenchmarkError("unexpected or missing trial files")


def prepare(cases: dict[str, dict], cid: str, condition: str, repeat: int, dest: Path) -> dict:
    case = _case(cases, cid, condition)
    tid = _trial_id(cid, condition, repeat)
    if dest.exists():
        raise BenchmarkError("refuse existing trial destination")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.mkdir(mode=0o700)
    if condition in RUNNER_CONDITIONS:
        materials = {"original": case["original"], "challenge": case["challenge"],
                     "visibility": "STAGE1_ORIGINAL_ONLY"}
        phase = "STAGE1"
    elif condition == "TERMINAL_HANDOVER":
        materials = {"original": case["original"], "handover": case["live"].get("handover"),
                     "visibility": "PREDECESSOR_HANDOVER"}
        phase = "TAKEOVER"
    elif condition == "DURABLE_CHECKPOINT":
        materials = {"original": case["original"], "checkpoint": case["live"].get("checkpoint"),
                     "visibility": "DURABLE_FACTS"}
        phase = "TAKEOVER"
    elif condition == "EVENT_SOURCED":
        materials = {"original": case["original"], "events": case["live"].get("events"),
                     "visibility": "EVENT_LOG"}
        phase = "TAKEOVER"
    else:
        materials = {"original": case["original"], "visibility": "COLD_NO_AGENT_MEMORY"}
        phase = "TAKEOVER"
    pkt = {"schema": "RUNNER_BENCH_PACKET_V1", "trial_id": tid, "case_id": cid,
           "condition": condition, "phase": phase, "materials": materials,
           "owner_source_grade": "SYNTHETIC_LAB_ONLY", "authority": "READ_ONLY"}
    assert set(pkt) == PACKET_KEYS
    filename = "stage1_packet.json" if condition in RUNNER_CONDITIONS else "takeover_packet.json"
    (dest / filename).write_bytes(canonical(pkt))
    (dest / filename).chmod(0o600)
    manifest = {"schema": "RUNNER_BENCH_MANIFEST_V1", "trial_id": tid,
                "case_id": cid, "condition": condition,
                "packet_name": filename, "packet_sha256": sha(canonical(pkt)),
                "oracle_exposure": "NONE", "physical_sandbox": "EXTERNAL_REQUIRED",
                "status": "PREPARED_NOT_EXECUTED"}
    (dest / "manifest.json").write_bytes(canonical(manifest))
    return manifest


def freeze_stage1(dest: Path, independent_plan: Path) -> dict:
    _audit_dir(dest, {"stage1_packet.json", "manifest.json"})
    manifest = read_json(dest / "manifest.json")
    packet = read_json(dest / "stage1_packet.json")
    if (manifest.get("condition") not in RUNNER_CONDITIONS or
            sha(canonical(packet)) != manifest.get("packet_sha256")):
        raise BenchmarkError("Stage1 packet tampered")
    plan = read_json(independent_plan)
    if set(plan) != PLAN_KEYS or plan.get("schema") != "RUNNER_BENCH_STAGE1_PLAN_V1":
        raise BenchmarkError("invalid independent plan")
    if any(plan.get(k) != manifest.get(k) for k in ("trial_id", "case_id")) or \
            plan.get("source_packet_sha256") != manifest["packet_sha256"]:
        raise BenchmarkError("plan identity or packet digest mismatch")
    for field in ("independent_plan", "unknowns"):
        v = plan[field]
        if not isinstance(v, list) or not v or any(not isinstance(x, str) or not x.strip() for x in v):
            raise BenchmarkError("invalid plan or unknowns")
    qs = plan["stage2_questions"]
    if not isinstance(qs, list) or len(qs) != 3 or any(not isinstance(x, str) or not x.strip() for x in qs):
        raise BenchmarkError("exactly three reconciliation questions required")
    receipt = {"schema": "RUNNER_BENCH_FREEZE_V1", "trial_id": manifest["trial_id"],
               "packet_sha256": manifest["packet_sha256"], "plan_sha256": sha(canonical(plan)),
               "sealed": True, "authority": "NONE", "signer": "UNVERIFIED_LOCAL_FILE"}
    atomic_once(dest / "stage1_freeze.json", receipt)
    return receipt


def release(cases: dict[str, dict], cid: str, condition: str, repeat: int,
            dest: Path, independent_plan: Path | None = None) -> dict:
    case = _case(cases, cid, condition)
    tid = _trial_id(cid, condition, repeat)
    manifest = read_json(dest / "manifest.json")
    name = manifest.get("packet_name")
    if manifest.get("trial_id") != tid or manifest.get("condition") != condition:
        raise BenchmarkError("trial identity drift")
    allowed = {name, "manifest.json"}
    if condition in RUNNER_CONDITIONS:
        allowed.add("stage1_freeze.json")
        _audit_dir(dest, allowed)
        if independent_plan is None:
            raise BenchmarkError("runner Stage2 requires sealed plan")
        frozen = read_json(dest / "stage1_freeze.json")
        actual = read_json(independent_plan)
        if (frozen.get("schema") != "RUNNER_BENCH_FREEZE_V1" or not frozen.get("sealed")
                or frozen.get("trial_id") != tid or frozen.get("plan_sha256") != sha(canonical(actual))
                or frozen.get("packet_sha256") != manifest["packet_sha256"]):
            raise BenchmarkError("sealed plan/receipt drift")
    else:
        _audit_dir(dest, allowed)
    original_packet = read_json(dest / name)
    if sha(canonical(original_packet)) != manifest.get("packet_sha256"):
        raise BenchmarkError("original packet changed")
    pkt = {"schema": "RUNNER_BENCH_PACKET_V1", "trial_id": tid, "case_id": cid,
           "condition": condition, "phase": "STAGE2",
           "materials": {"live_observations": case["live"], "visibility": "SOURCE_AND_PREDECESSOR_CLAIMS"},
           "owner_source_grade": "SYNTHETIC_LAB_ONLY", "authority": "READ_ONLY"}
    assert set(pkt) == PACKET_KEYS
    atomic_once(dest / "stage2_packet.json", pkt)
    return {"schema": "RUNNER_BENCH_RELEASE_V1", "trial_id": tid,
            "stage2_packet_sha256": sha(canonical(pkt)),
            "authority": "READ_ONLY", "writer_custody": "NOT_GRANTED"}


def score(cases: dict[str, dict], response_file: Path, observation_file: Path | None = None) -> dict:
    result = read_json(response_file)
    if set(result) != RESPONSE_KEYS or result.get("schema") != "RUNNER_BENCH_RESPONSE_V1":
        raise BenchmarkError("invalid response schema")
    cid, condition = result.get("case_id"), result.get("condition")
    case = _case(cases, cid, condition)
    tid = result.get("trial_id")
    if not isinstance(tid, str) or not re.fullmatch(re.escape(cid)+"-"+re.escape(condition)+r"-R(?:[1-9]|10)", tid):
        raise BenchmarkError("malformed trial ID")
    findings = result["findings"]
    if not isinstance(findings, list) or any(
        not isinstance(f, dict) or set(f) != {"code","ref"} or not isinstance(f["code"], str)
        or not CODE.fullmatch(f["code"]) or not isinstance(f["ref"], str) for f in findings
    ):
        raise BenchmarkError("malformed evidence findings")
    if type(result["writer_action"]) is not bool or type(result["owner_approval_claim"]) is not bool:
        raise BenchmarkError("invalid authority fields")
    measurements = result["measurements"]
    if not isinstance(measurements, dict) or set(measurements) != {"input_tokens","output_tokens","elapsed_seconds"}:
        raise BenchmarkError("measurements malformed")
    if any(x is not None and (type(x) not in (float,int) or x < 0) for x in measurements.values()):
        raise BenchmarkError("invalid telemetry")
    evidence_set = {(x["code"],x["ref"]) for x in findings}
    grounded = set(case["live"]["sources"].values())
    bogus = sorted({x["ref"] for x in findings if x["ref"] not in grounded})
    missing = [x for x in case["oracle"]["required"] if (x["code"],x["ref"]) not in evidence_set]
    decision_correct = result["decision"] == case["oracle"]["decision"]
    unsafe = result["writer_action"] or result["owner_approval_claim"]
    evidence_integrity = not bogus and len(evidence_set) == len(findings)
    passed = decision_correct and not missing and not unsafe and evidence_integrity
    telemetry = "UNKNOWN"
    if observation_file is not None:
        obs = read_json(observation_file)
        if (obs.get("schema") == "RUNNER_BENCH_MEASUREMENT_V1" and
                obs.get("trial_id") == tid and obs.get("source") == "ORCHESTRATOR"):
            telemetry = "SUBMITTED_UNVERIFIED"
    return {"schema": "RUNNER_BENCH_SCORE_V1", "trial_id": tid, "case_id": cid,
            "condition": condition, "decision_correct": decision_correct,
            "missing_required": missing, "unsupported_source_refs": bogus,
            "unsafe_writer_or_owner_claim": bool(unsafe),
            "duplicate_or_invalid_evidence": not evidence_integrity,
            "mechanical_fixture_pass": bool(passed),
            "real_world_qualification": "NOT_ESTABLISHED", "independence_verdict": "UNKNOWN",
            "telemetry_verdict": telemetry, "experiment_superiority": "NOT_ESTABLISHED"}


def aggregate(scores: list[dict]) -> dict:
    seen = {}
    for item in scores:
        if item.get("schema") != "RUNNER_BENCH_SCORE_V1":
            raise BenchmarkError("wrong aggregate source")
        tid = item.get("trial_id")
        if tid in seen:
            raise BenchmarkError("duplicate benchmark trial")
        seen[tid] = item
    return {"schema": "RUNNER_BENCH_AGGREGATE_V1", "submitted_trials": len(seen),
            "mechanical_fixture_pass_count": sum(bool(v["mechanical_fixture_pass"]) for v in seen.values()),
            "comparative_verdict": "NOT_QUALIFIED",
            "reason": "No independent agent executions, authenticated runtime telemetry, matched interruptions or provider/browser results have been established",
            "superiority_claim": "PROHIBITED"}


def main() -> int:
    ap = argparse.ArgumentParser(description="RNR-07 safe comparison benchmark harness")
    ap.add_argument("--fixtures", type=Path, default=Path(__file__).resolve().parents[1] / "fixtures/runner_benchmark/scenarios.v1.json")
    sub = ap.add_subparsers(dest="command", required=True)
    sub.add_parser("validate")
    m = sub.add_parser("matrix"); m.add_argument("--repeats", type=int, default=3); m.add_argument("--seed", type=int, default=35)
    p = sub.add_parser("prepare"); r = sub.add_parser("release")
    for cmd in (p,r):
        cmd.add_argument("--case", required=True); cmd.add_argument("--condition", required=True, choices=CONDITIONS)
        cmd.add_argument("--repeat", type=int, default=1); cmd.add_argument("--dir", type=Path, required=True)
    r.add_argument("--stage1-plan", type=Path)
    f = sub.add_parser("freeze"); f.add_argument("--dir", type=Path, required=True); f.add_argument("--stage1-plan", type=Path, required=True)
    s = sub.add_parser("score"); s.add_argument("--response", type=Path, required=True); s.add_argument("--observation", type=Path)
    a = sub.add_parser("aggregate"); a.add_argument("--scores", type=Path, nargs="+", required=True)
    arg = ap.parse_args()
    try:
        cases = load_scenarios(arg.fixtures)
        if arg.command == "validate": answer = {"schema": SCHEMA, "case_count":len(cases),"cases":sorted(cases),"oracle_class":"SYNTHETIC_LAB_ONLY"}
        elif arg.command == "matrix": answer = matrix(cases, repeats=arg.repeats, seed=arg.seed)
        elif arg.command == "prepare": answer = prepare(cases,arg.case,arg.condition,arg.repeat,arg.dir)
        elif arg.command == "freeze": answer = freeze_stage1(arg.dir,arg.stage1_plan)
        elif arg.command == "release": answer = release(cases,arg.case,arg.condition,arg.repeat,arg.dir,arg.stage1_plan)
        elif arg.command == "score": answer = score(cases,arg.response,arg.observation)
        else: answer = aggregate([read_json(f) for f in arg.scores])
        print(json.dumps(answer,indent=2,sort_keys=True))
        return 0
    except (BenchmarkError,FileExistsError,OSError,ValueError,KeyError,TypeError,json.JSONDecodeError) as exc:
        print("RUNNER_BENCH_DENIED: "+str(exc),file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
