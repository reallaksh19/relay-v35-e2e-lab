# Expected outcomes, grading and objective stress-test oracles

**Scope:** `Common#875`, exactly `Common@13989969f6b7e432c4f7c1ddfe975449dba53593`, disposable PRIVATE lab only. This is an **experiment task status**, never a hand-written programme DELP percentage. A simulator/fixture checks one contract boundary but **cannot qualify the provider-backed end-to-end path**.

| Task | Minimum *expected* source-backed result | Required artifact / proof | Correct classification if absent or broken |
| --- | --- | --- | --- |
| T00 | Bash scripts pass `bash -n`; Python scripts compile; harness expected to pass; feature tests fail due unimplemented parser/report (expected RED) | Sanitized per-command logs, exact exits, names of errors; ZIP/file SHA | PASS for preflight only when harness pass and app RED cause confirmed. Otherwise FAIL |
| T01-PREFLIGHT | 7 independent hermetic tests covering private target, wrong identity, partial creation, repeated run and auth guard | Separate simulator stdout/exit/hash, source test version | SIMULATED_ONLY PASS; not actual repo provisioning |
| T01 | Authenticated private repo exists; exactly 3 real issues with distinct refs; map and graph match GitHub; graph committed to current main | Repo GET with visibility; issue GET; exact main SHA and graph digest; no secrets | BLOCKED if no gh rights/repo; FAIL if public, duplicates or mismatched refs |
| T02 | DELP CLI graph validation, ENFORCED decomposition and initial project succeed at pinned Common SHA | Actual command logs; SHA of canonical projection; ref/repository cross-check | FAIL if fixture invalid, do not weaken DELP |
| T03 | GitHub Actions matrix actually runs on recorded SHA; harness pass, feature tests fail for intended NotImplementedError only | Workflow run+job URLs and log lines, checked HEAD, missing/unknown checks explicit | EXPECTED_RED if precise cause; FAIL for unexpected cause, BLOCKED if no run |
| T04 | PR A actually created with correct base/head; U01/U02 code/evidence; U03 remains undone on purpose | PR+commit URLs, tests, unit evidence, interruption point | FAIL if counterfeit material; BLOCKED if repo/CI unavailable |
| T05 | Fresh session reconstructs R1 correctly from issue-only entry and finishes U03 on same responsibility | Separate session witness, reconstruct comparison, PR HEAD transition, new exact CI/evidence | FAIL if wrong unit/context or old evidence promoted; BLOCKED if no independent executor |
| T06 | Independent source reviewer submits PASS/REPAIR/FAIL with material SHA; merge only via explicit scoped authorization | Reviewer principal and source/read record; distinct execution; exact PR HEAD | REVIEW_NOT_QUALIFIED if author-self-review; no merge assumed |
| T07 | PR B obeys parser dependency and passes sorted Decimal/CLI tests with full evidence | PR+CI+review; separate U01/U02/U03 records | BLOCKED if parser dependency unresolved; FAIL for material mismatch |
| T08 | Three physical paths traced: V3.2 C6→DELP positive, R3→R12→R9→R11→R4 native candidate path, V3.5 read-only path; missing R3B→DELP explicitly detected | Actual call graph/run traces at pinned source; exact projection/consumer digests | EXPECTED_RED for missing programme join; no full E2E PASS |
| T09 | Dry run makes 0 writes; without source and scoreboard approvals `--apply` denied; authorized scoped sandbox test only when external grant exists | Before/after provider readback; auth receipt/scope; exact request HEAD | PASS for denied/no-write oracle; BLOCKED for optional live apply if approval absent |
| T10 | Each S01–S16 run yields its own expected/observed case record. Unknown and forged facts fail closed | 16 signed-off case rows, source links, commands and candidate SHAs | PARTIAL/BLOCKED/FAIL per case; don't replace with one green count |
| T11 | 4 cold sessions (parent, child, PR, repo) independently reconstruct Owner *synthetic* source, graph, facts, material and next | Four distinct contexts/provenance, independent oracle, contradiction table | BLOCKED if no distinct executions; FAIL for unsupported/conflicting source truth |
| T12 | Aggregate truthful status of prior tasks, real graph/CI/review and source cut-set with uncertainty | `TASK_RESULT`, links to each task, ledger integrity check, contradictions and blockers | `V35_R14_E2E_NOT_QUALIFIED` until actual WP0+WP1–WP8 standards met |

## Required grades must remain orthogonal

- **Task result:** `PASS / EXPECTED_RED / FAIL / BLOCKED / NOT_RUN` (separate `SIMULATED_ONLY` provenance flag).
- **GitHub observation:** `PROVIDER_OBSERVED`, `INJECTED`, `SYNTHETIC`, `UNKNOWN` and source/read-window identity.
- **CI:** `PASS / FAIL / PENDING / UNKNOWN` at exact required head; selected CI is not by itself a required-check or reviewer verdict.
- **Evidence:** `CURRENT_UNDER_VERSIONED_POLICY / STALE / UNQUALIFIED / UNKNOWN`. Never equate syntactically valid CHECKPOINT_FACTS with independently accepted evidence.
- **Reviewer:** `INDEPENDENT_PASS / REPAIR / FAIL / NOT_SUBMITTED / INDEPENDENCE_NOT_PROVEN`.
- **Owner source:** `SYNTHETIC_LAB_ONLY`; no real chat-source authentication.
- **Writer/merge:** `OFF` absent explicit separately scoped approval; even a clean GitHub mergeable state is not a reviewer verdict.

## Three non-interchangeable source identities

1. `PLAN_GRAPH_REVISION`: released graph commit + immutable graph bytes/digest.
2. `SESSION_SOURCE_COMMIT`: committed session/custody source SHA when a RELAY source is used.
3. `CODE_CANDIDATE_HEAD`: exact PR head from GitHub; a new push invalidates previous candidate-currentness.

Record repository and role for every SHA. Equality is never a universal requirement. A forged role or SHA-based attestation is a stress failure.

## Negative stress cases S01–S16

Refer to `docs/stress-matrix.md` for full steps. For each case record: case ID, input mutation, material basis/head, independent source URLs, expected state, observed state, actual command/exit, replayability, source grade, reviewer grade, PASS/FAIL/BLOCKED/NOT_RUN and a link to the specific evidence comment. Required invariants: no progress inflation by author percentages, no evidence current on stale or FAILED material, no Owner authentication from comments, no native provenance from recomputable digest, no independent-review claim from same principal, no stale handover reuse, no title-writing without scoped and nonrevoked approval, and no divergent parent/child/PR/cold snapshot falsely reported as canonical.

## Cold successor oracle

Each successor, given **only one link**, must accurately reconstruct repo/root/leaf/PR identity, exact plan revision, current code head, unit truth, accepted facts, reviewer/CI/Owner grades, next authorized action, and unknowns. Record a contradiction matrix across all 4. A single correct parent-only result does not qualify child, PR or repo-only entry. Do not use the predecessor chat as hidden context.
