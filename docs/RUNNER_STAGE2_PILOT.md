# RNR-04 — Stage 2 Source-First Reconciliation (LAB only)

Status: experimental, read-only, no execution admission or Owner/reviewer authority. Implements only source reconciliation in lab issue #9; does not complete Common #787, Common #864 WP0, or lab #6 end-to-end lifecycle acceptance.

## Core guarantees

1. Verify the frozen Stage 1 bundle/plan receipt before reading current implementation. Recheck allowlisted baseline file digests against immutable Git blobs at the starting commit.
2. Read actual Git HEAD, branch, ancestor relationship and all tracked/unstaged/staged/untracked paths. Flag incomplete and out-of-scope changes.
3. Observe the origin branch with Git ls-remote; distinguish MATCH, DIVERGED and UNAVAILABLE. This observation does NOT prove that origin is an authenticated or approved GitHub remote.
4. Planned takeover: compare Agent A's handover claims against Runner B's sealed independent plan and actual repository state. Never accept completion claims without native tests/exact-head evidence.
5. Emergency takeover: no handover needed. Reconstruct source state, retain uncertainty and HOLD where source is ambiguous.
6. Even clean source reconciliation produces SOURCE_RECONCILED_READ_ONLY, not execution permission, source owner authentication, approval, verified evidence or DELP progress. Writer authorization is always DENIED.

## CLI

    python scripts/runner_stage2.py \
      --bundle /isolated/runner-stage1 \
      --plan /isolated/runner-plan.json \
      --receipt /controller/runner-freeze.json \
      --repo /worktrees/lab-r1

For planned takeover add --handover /controller/agent-A-handover.json.

Inputs: frozen RUNNER_RECONSTRUCTION_V1 plan, RUNNER_RECONSTRUCTION_FREEZE_V1 receipt and pinned Stage 1 source bundle; actual Git repository; optional RUNNER_PRIMARY_HANDOVER_V1 file.

Handover fields are strictly restricted: schema, responsibility, starting_commit, candidate_head, branch, proposed_next_responsibility, proposed_plan, completed_claims, known_issues.

Output RUNNER_RECONCILIATION_V1: planned/emergency mode, baseline/HEAD/branch and dirty/diff/out-of-scope paths, remote verification, source issues, plan discrepancies, parked medium ROI, draft-only continuation issue update, unknown evidence qualification, denied writer custody.

## Fail-closed oracles

- No handover: emergency source-first mode.
- Stale handover SHA: HANDOVER_HEAD_STALE.
- Remote branch divergence/missing origin: REMOTE_NOT_CURRENT.
- Uncommitted/partial work: UNCOMMITTED_MATERIAL.
- Unrelated R2 reporter changes: OUT_OF_SCOPE_MATERIAL.
- Agent A proposes LAB-R2: HANDOVER_SCOPE_EXPANSION, Owner decision required.
- Tampered Stage 1 plan: hard rejection.
- Agent A claims completed units: UNVERIFIED_CLAIMS.
- All source checks passed: read-only reconciliation only; no implicit authority.

## Tests

    python -m py_compile scripts/runner_pilot.py scripts/runner_stage2.py
    python -m unittest discover -s tests -p 'test_runner*.py' -v

The 14 new Stage 2 tests use genuine temporary local Git repositories and bare origin remotes, including commits/pushes/dirty worktrees, not an invented provider response. These tests do NOT prove real GitHub provenance or GitHub provider authorization.

## Explicitly not implemented

Stage 1 agent tool sandboxing, monotonic writer epoch/fencing and credential revocation (RNR-05), GitHub native issue publication, verified Owner/reviewer decisions, CI acceptance, automated Runner C spawn, and controlled comparator experiment. The Stage 2 read model is not the custody service. It cannot grant write access.
