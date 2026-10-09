# TASK_EVIDENCE — Tnn — [PASS | EXPECTED_RED | FAIL | BLOCKED | NOT_RUN]

**Purpose:** copy this record only after actual task execution. Never check a box solely from agent notes or test counts seen in a GitHub description. This is a **task evidence** publication, not an authenticated reviewer verdict or programme DELP P/E.

- **Source programme:** `reallaksh19/Common#787 → #864 → #875 → #877`
- **Task ID / scope:** `Tnn / <exact bounded responsibility>`
- **Operator / session:** `<asserted principal and distinct session ref>`
- **Execution mode:** `NATIVE_PROVIDER / LOCAL_NATIVE / SIMULATED_ONLY / FIXTURE_ONLY / NOT_RUN`
- **Execution timestamp UTC:** `<actual clock>`
- **Protocol pin:** `reallaksh19/Common@13989969f6b7e432c4f7c1ddfe975449dba53593`
- **Lab repository:** `reallaksh19/relay-v35-e2e-lab`, PRIVATE status `<provider observed or UNKNOWN>`
- **Parent / child / PR refs:** `<actual canonical refs, else NOT_CREATED>`
- **Graph revision role and SHA:** `<PLAN_GRAPH_REVISION, immutable ref and SHA or UNKNOWN>`
- **Session source role and SHA:** `<SESSION_SOURCE_COMMIT or NOT_PRESENT>`
- **Candidate role and SHA:** `<CODE_CANDIDATE_HEAD or NOT_PRESENT>`
- **Graph digest / input digest / snapshot digest:** `<computed by canonical source, NEVER hand-authored>`
- **CI policy version and required check source:** `<actual source or UNKNOWN>`
- **Evidence policy version:** `<e.g. V3.2 documented semantics; not self-invented stronger claim>`
- **Owner original source:** `SYNTHETIC_LAB_ONLY`
- **Reviewer principal/verdict:** `<separately sourced or INDEPENDENCE_NOT_PROVEN>`
- **Write/merge grant:** `NONE` unless separate explicit scoped, provider-verified approval

## Completed task checklist

- [ ] Source and task scope independently inspected
- [ ] Actual commands and exit codes captured, and sanitization reviewed
- [ ] Intended positive control and negative oracle executed when task requires them
- [ ] GitHub observations match intended repo/ref/HEAD (or explicitly unavailable)
- [ ] Expected vs observed compared against `docs/EXPECTED_OUTCOMES.md`
- [ ] Rejected/unknown/stale material preserved rather than forced to PASS
- [ ] Evidence log and artifact SHA256 recalculated after redaction
- [ ] GitHub issue comment published as a **new** TASK_EVIDENCE entry (or BLOCKED)
- [ ] Exact comment read back via GitHub GET (or not done / BLOCKED)
- [ ] New local audit ledger event appended and chain verified

## Expected behavior

`<Detailed oracle BEFORE test. Cite the declared graph/test/protocol source.>`

## Observed behavior

`<What the actual runtime produced, with exact status/exit, count, failures and skipped tests or UNKNOWN.>`

## Native source and command evidence

| Command / action | Source HEAD | Exit / provider state | Log / artifact SHA256 | GitHub URL (if observed) |
| --- | --- | --- | --- | --- |
| `<command>` | `<SHA/UNKNOWN>` | `<exit/status>` | `<sha256>` | `<URL/NOT_CREATED>` |

## Case or call-edge findings

| ID | Expected | Observed | Result | Basis |
| --- | --- | --- | --- | --- |
| `<Tnn/Snn>` | `<falsifiable assertion>` | `<source-linked observation>` | `<PASS/FAIL/BLOCKED>` | `<exact source URL and HEAD>` |

## Truth / unknowns / deviations

`<Unknown provider pages, unexecuted CI, uncertain reviewer independence, source-authentication status, stale facts, tool limitations, partial creation and any code/plan deviation.>`

## Verdict & continuation

- **Bounded task verdict:** `<PASS | EXPECTED_RED | FAIL | BLOCKED | NOT_RUN>`
- **V3.5-R14 E2E acceptance:** `NOT_QUALIFIED` unless separately independently proven
- **Programme #787 AC:** `AC0/8` until independent programme acceptance (do not update from task)
- **Next permitted task / stop condition:** `<Tnn or exact missing permission>`
- **Supersedes or corrects:** `<prior issuecomment link, if any>`

## Publication and audit proof

- **Local evidence draft SHA256:** `<digest>`
- **GitHub issue comment:** `<exact https://github.com/reallaksh19/Common/issues/875#issuecomment-... or NOT_PUBLISHED>`
- **Provider readback:** `<GET endpoint, timestamp, observed body digest, match TRUE/FALSE; or NOT_RUN>`
- **Local audit events:** `<seq/hash for TASK_EVIDENCE_DRAFTED, GITHUB_PUBLISHED, GITHUB_READBACK_VERIFIED>`. A ledger hash is integrity, never a human identity receipt.
