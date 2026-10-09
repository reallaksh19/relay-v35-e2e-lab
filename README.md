# V3.5-R14 E2E Lab — Campaign A (expected RED)

**Local agent: START WITH [`AGENT_START_HERE.md`](AGENT_START_HERE.md).** It contains the complete copy-ready prompt, exact allowed scope, T00–T12 expected outcomes, stop conditions, and the per-task GitHub publication/readback/audit procedure. Do not treat the package as a live execution report.


This **private, disposable** GitHub repository tests the *real* engineering lifecycle against `reallaksh19/Common` rather than validating a synthetic nine-surface fixture. It is a test artifact, not a claim that V3.5-R14 is integrated, independently reviewed or approved.

## Immutable protocol basis

- Source: `reallaksh19/Common@13989969f6b7e432c4f7c1ddfe975449dba53593`
- Governing integration plan: https://github.com/reallaksh19/Common/issues/864
- Independent architecture review: https://github.com/reallaksh19/Common/issues/866 — pending
- Prior R12 source review: https://github.com/reallaksh19/Common/issues/869 — pending
- Production writers/automatic merging/Owner original-chat authentication: **OFF / NOT PROVEN**
- This lab's Owner prompt is a **synthetic lab-only instruction**; do not relabel it as authenticated original chat evidence.

## Design

Feature A: strict CSV parser (`src/inventorylab/parser.py`, parser tests).
Feature B: deterministic JSON report (`src/inventorylab/report.py`, reporter tests), dependent on A.

The two functions are intentionally `NotImplementedError` in Campaign A. The application test suite must be **RED** before feature PRs are written; the independent harness self-test must be **GREEN**. Never treat red application tests as an infrastructure failure or count them as completed tasks.

## Setup — one authorized local invocation

Prerequisites: `git`, `gh` authenticated with repository-creation rights for the desired owner, Python 3.11+, PyYAML, and the local repository copy extracted here. Default repo is `reallaksh19/relay-v35-e2e-lab`.

```bash
python -m pip install PyYAML
bash scripts/bootstrap_lab.sh reallaksh19/relay-v35-e2e-lab
```

The bootstrap creates the **private** repository (if the caller's GitHub permissions allow it), first commit, parent programme issue, two bounded child issues, and a graph with the **actual** GitHub issue numbers. It makes no merge, approval or source-scope grant. Review generated `.relay/graph.yaml` and issue links before any subsequent activity.

For source-level checks clone Common alongside the lab and pin it:

```bash
git clone https://github.com/reallaksh19/Common.git ../Common
git -C ../Common checkout 13989969f6b7e432c4f7c1ddfe975449dba53593
bash scripts/run_baseline.sh
```

`run_baseline.sh` checks the pinned Common revision, validates the canonical DELP graph, checks decomposition, and generates an initial uncredited projection. No GitHub writes.

## Actual engineering experiment

1. Create **draft PR A** from branch `lab/parser`. Agent A completes parser U01/U02, posts a `TASK_EVIDENCE` block with real issue refs, PR head SHA and CI refs. Then interrupt the agent and cold-resume U03 on the *same child issue* in another execution.
2. Create **draft PR B** from branch `lab/report`, based on main only after A merges (or explicitly model A's immutable dependency). Agent B implements reporter U01/U02/U03 and posts its own evidence. Do not mark test PASS before GitHub Actions completes at exact PR head.
3. Compare `project`, `admit`, `frontier`, `frontier-verify`, `sync-github --dry-run`, V3.5 `integration_cold_entry_v35.py` and `integration_relay_consumers_v35.py` on actual GitHub issue/PR state. Unapproved cold entry must report HOLD, not success.
4. Do not enable `sync-github` or `integration_scoreboard_publish_v35 --apply` until distinct **sandbox-only**, scoped graph and scoreboard approvals have been verified. Keep default GitHub Actions permissions read-only.
5. Run negative tests S01–S16 from `docs/stress-matrix.md` and record results as `PASS / FAIL / NOT_RUN / BLOCKED` with separate expected and observed evidence, never inferred PASS.
6. Run four genuinely isolated cold successor executions: parent-only, child-only, PR-only, repository-only. Each produces a structured independent reconstruction, compared against the material oracle; no copied context.

## Local reproducible tests

```bash
PYTHONPATH=src python -m unittest discover -s tests -p 'test_harness*.py' -v
PYTHONPATH=src python -m unittest discover -s tests -p 'test_inventory*.py' -v
```

Expected at baseline: harness pass; inventory tests fail because the implementation is intentionally absent. Turn the red inventory tests green **only through the two feature PRs**.

## Evidence policy

- `P` = declared unit completion under the selected canonical DELP policy; `E` = current policy-qualified evidence, **not** independent review or Owner acceptance.
- Do not equate `PLAN_GRAPH_REVISION`, `SESSION_SOURCE_COMMIT`, `CODE_CANDIDATE_HEAD`.
- Never infer Owner-authored source, external acquisition witness, independent reviewer, publication authorization, or a material merge from an agent's JSON/digest.
- Existing V3.2 DELP/C6 path is live; the Node RELAY R3/R12/R9/R11/R4-to-programme-DELP join is missing. The E2E test is designed to detect that gap, not conceal it.

See `docs/stress-matrix.md` and `docs/experiment-log-template.md` for the negative oracle and publication template.

## Common tracking record

The cross-repository Campaign A execution issue is [Common #875](https://github.com/reallaksh19/Common/issues/875). Its current status is **LAB_REPOSITORY_NOT_CREATED** until GitHub provisioning is independently verified; this local ZIP does not create GitHub issues or prove a full lifecycle pass.

## Local agent task-by-task evidence (Campaign A)

See [`docs/LOCAL_AGENT_TASKS.md`](docs/LOCAL_AGENT_TASKS.md) for T00–T12 with checkboxes, handoff gates, exact source-of-truth requirements, evidence generator instructions and one new `TASK_EVIDENCE` comment on [Common #875](https://github.com/reallaksh19/Common/issues/875) **after each task**. A local agent can begin T00 immediately without GitHub. T01 and later require the PRIVATE lab repository to exist.

The `scripts/task_evidence.py` generator is intentionally read-only and refuses `PASS` when any attached command transcript has a nonzero exit, and refuses `EXPECTED_RED` if no nonzero exit is recorded. A digest authenticates neither the agent nor GitHub; reviewer and provider checks remain separate.

## T01 hermetic preflight (offline; not a GitHub repo)

`tests/test_harness_bootstrap.py` tests the **real** `scripts/bootstrap_lab.sh` in temporary folders using stub `gh`/`git` binaries. This checks the one-shot and interruption behavior without credentials or remote writes. On slower systems, run its seven cases in the two batches listed in `evidence/T01-SIMULATED.md` to avoid runner timeouts. The bootstrap now **only permits** `reallaksh19/relay-v35-e2e-lab`; passing these tests does not demonstrate actual private repository creation, owner authorization, Actions, or DELP source compliance. Live T01 remains blocked until real GitHub readback.

## V3 independently auditable handoff

- [`AGENT_START_HERE.md`](AGENT_START_HERE.md): primary instructions to the local agent.
- [`docs/EXPECTED_OUTCOMES.md`](docs/EXPECTED_OUTCOMES.md): task verdict and independent source oracles.
- [`docs/TASK_EVIDENCE_TEMPLATE.md`](docs/TASK_EVIDENCE_TEMPLATE.md): full per-task publication form, with source roles, evidence and readback.
- [`docs/AUDIT_TRAIL_SPEC.md`](docs/AUDIT_TRAIL_SPEC.md): external GitHub comments plus local append-only hash chain, threat model and limitations.
- [`docs/AUDIT_INDEX.md`](docs/AUDIT_INDEX.md): initial GitHub record links and source truth.
- [`scripts/audit_trail.py`](scripts/audit_trail.py): append/verify local audit journal; hashes provide integrity, **not** authenticated identity or accepted evidence.
- [`scripts/verify_github_comment.py`](scripts/verify_github_comment.py): provider GET, exact issue/comment author/body readback; still not independent reviewer certification.
- [`PACKAGE_MANIFEST.sha256`](PACKAGE_MANIFEST.sha256): check exact shipped bytes with `sha256sum -c` before changing any files. The ZIP checksum is published separately in Common #875/#877.

After each task, the independent local agent must publish a new `TASK_EVIDENCE — Tnn` to Common #875 and independently read it back. For missing GitHub access, preserve the draft, mark BLOCKED and do not claim publication. Existing T00 and simulated T01 records are from the author-side scaffold run and **do not qualify** independent local-agent tests.
