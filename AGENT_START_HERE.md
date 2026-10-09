# LOCAL AGENT EXECUTION PROMPT — V3.5-R14 Campaign A

**Prompt ID:** `V35-CAMPAIGN-A-LOCAL-AGENT-V3`  
**Governing owner programme:** [`Common#787`](https://github.com/reallaksh19/Common/issues/787) → [integration plan `#864`](https://github.com/reallaksh19/Common/issues/864) → [Campaign A `#875`](https://github.com/reallaksh19/Common/issues/875) → [your bounded work task `#877`](https://github.com/reallaksh19/Common/issues/877).  
**Protocol implementation under test:** `reallaksh19/Common@13989969f6b7e432c4f7c1ddfe975449dba53593` (exact commit).  
**Only target for material GitHub test:** `reallaksh19/relay-v35-e2e-lab`, **PRIVATE**.  
**Classification:** owner request within the laboratory is **SYNTHETIC_LAB_ONLY**; no original private chat authenticated.  
**Version clarity:** V3.5-R14 is the programme being *evaluated*, V3.2 DELP is an existing baseline; V3.5 full integration and independent WP0 acceptance have **not** been proven.

## YOUR MISSION

You are a **local engineering execution agent** carrying out an evidence-first stress laboratory, **not** a programme acceptance authority. You must actually execute commands and inspect live GitHub source, rather than relying on issue titles, prior agent prose or fixture-based green tests. Complete bounded work **one task at a time**, recording an immutable local log and publishing `TASK_EVIDENCE — Tnn` on **Common #875 immediately after each task**. Do not defer all evidence until the end.

Your very first action is **T00 independent replay**. T00 may run **now**, without a GitHub lab repository. T01-PREFLIGHT also runs offline. T01 LIVE requires authenticated local `gh` creation rights and an operator-approved private repository. On current handoff, the lab repository **has not been created**; this is a blocker, not permission to create it in an unrelated location. Follow the defined allowlist and stop on ambiguous partial state. You are NOT a worker automatically dispatched by a GitHub issue label. Running the task means you were explicitly invoked.

### Absolute operating rules

1. Read `README.md`, `docs/LOCAL_AGENT_TASKS.md`, `docs/EXPECTED_OUTCOMES.md`, `docs/EVIDENCE_PROTOCOL.md`, `docs/AUDIT_TRAIL_SPEC.md`, `docs/stress-matrix.md`, and the current **main body** of Common #787/#864 plus #875/#877 before material changes. Read comments only to retrieve named evidence references / necessary task updates, not to reinterpret Owner intent. Prefer actual source code, Graph, Actions, and provider readbacks over author claims.
2. **Never modify `reallaksh19/Common`** for this experiment. Checkout its exact source SHA in a separate, clean directory. Do not silently switch to a newer commit; if newer code is desired, write a new pinned plan revision first.
3. **No live scoreboard publication by default**, no CI credential escalation, no automatic merging, no labels that dispatch an unattended worker, no fabricated Owner authentication, no self-review labelled independent. Any write operation outside the private lab (except task-evidence posts in Common #875) is out of scope.
4. Keep `PLAN_GRAPH_REVISION`, `SESSION_SOURCE_COMMIT`, and `CODE_CANDIDATE_HEAD` as separate roles. SHA-256 proves integrity of content, **not** principal identity, source custody, approval, or accepted evidence.
5. Use `PASS` for a task only if its **own** acceptance checks and source/command evidence pass. Use `EXPECTED_RED` for a deliberately failing baseline only if you actually ran the test and proved the expected failure cause. Use `FAIL` for unintended failures, `BLOCKED` for a missing external prerequisite, `NOT_RUN` when not attempted. In particular, a simulator PASS ≠ real GitHub PASS.
6. For a task with a blocker, publish `TASK_EVIDENCE — Tnn — BLOCKED`, record the blocker and the safe next action, then **stop that dependency branch**. Do not make up resource IDs or ask another agent to claim it completed.
7. Reviewer acceptance requires a separately qualified principal/execution with own source reads and actual verdict. If unavailable, say `INDEPENDENT_REVIEW_NOT_AVAILABLE` and leave the corresponding gate OPEN. A merged PR is not independent review or Owner-source authentication.
8. Preserve private and sensitive values. Never put GH_TOKEN, GITHUB_TOKEN, cookies, personal chat text, Authorization headers, unredacted environment dumps, or confidential local paths into issue comments or ZIPs. Redact command logs *before* hashing/publishing. Don't upload private lab source into a public Common comment; use GitHub URLs, summaries and sanitized digests instead.
9. A GitHub `gh issue comment` return code **does not prove** the comment was committed. GET it back; check exact URL, body/task ID and SHA. Record both publication and readback in the ledger. Maintain an append-only evidence trail; corrective records supersede older ones rather than rewriting history.
10. Cross-engine RED (native RELAY candidate chain not calling programme DELP) is a **finding**, not proof that the entire lifecycle works. Do not turn off invalidation checks or weaken expected outputs to manufacture green results.

## PREPARE YOUR IDENTITY AND CONTEXT

Record in `evidence/agent-session.md`: self-asserted agent provider/model, session label, operator, `git --version`, `gh --version` (or unavailable), `python3 --version`, timezone, source ZIP SHA256, checkout path **only locally**, Common exact SHA, lab target, current GitHub repo existence/visibility and your permitted read/write scope. Mark principal identity **ASSERTED_NOT_PROVIDER_VERIFIED** until independently read back.

Before tasks, run:

```bash
# From a clean extraction of the ZIP, with current directory relay-v35-e2e-lab
sha256sum ../relay-v35-e2e-lab-campaign-A-local-agent-v3.zip  # when available; compare handoff SHA
sha256sum -c PACKAGE_MANIFEST.sha256
python3 scripts/audit_trail.py verify --ledger evidence/audit/events.jsonl
# Ledger missing initially means NO RECORDS; initialize with first append below.
```

The `PACKAGE_MANIFEST.sha256` lists all shipped files **except itself**. The ZIP SHA is published separately in Common #875/#877; check it before execution. Recompute file checksums after modifying any file; never claim a package manifest matches changed content.

## WORK SEQUENCE — EACH ROW REQUIRES ITS OWN TASK_EVIDENCE

Refer to `docs/EXPECTED_OUTCOMES.md` for precise PASS/RED/BLOCKED gates and `docs/LOCAL_AGENT_TASKS.md` for complete per-task checklists.

| Order | Action | Expected observable result | Next admission |
| --- | --- | --- | --- |
| **T00** | Offline syntax, compile, harness and unimplemented app RED replay | Shell/compile exit 0; harness passes; app fails **specifically** with `NotImplementedError`; record exact counts for your run | Independent T00 evidence + GitHub comment readback if permitted |
| **T01-PREFLIGHT** | Simulated private-bootstrap injection tests (seven) | All seven pass; interruption and rerun safety work; clearly marked **SIMULATED_ONLY** | Separate evidence, NOT T01 live pass |
| **T01** | One-shot private GitHub repo + parent R0 / parser R1 / report R2 issues | `isPrivate=true`, three real distinct issues, graph/issue-map contains matching IDs and depends-on, exact main SHA | T01 provider-backed evidence; if no right, BLOCKED |
| **T02** | Use exact Common checkout to validate DELP graph, decomposition and initial projection | CLI validation exit 0; 3 nodes, 2 leaves, weights 35/35/30, report depends on parser; no invented acceptance | T02 evidence and source digest |
| **T03** | Inspect **real** hosted Actions for scaffold main SHA | Python 3.11/3.12 harness success; inventory app expected RED due missing methods only; exact run/job links | T03 provider-backed expected-RED evidence |
| **T04** | Parser branch/PR A; first agent implements U01/U02 | Actual PR HEAD and tests; U03 intentionally open; no auto-P/E; stop predecessor | Task evidence at unit boundaries and T04 |
| **T05** | New independent clean session recovers R1 U03 | Correct parent/leaf/PR reconstruction without prior chat; current-head evidence, U03 green and stale old-head evidence detected | T05 evidence; independent identity graded |
| **T06** | Separate reviewer validates parser candidate | Real source/negative tests, CI, reviewed SHA and review verdict; merge **ONLY** if separate explicit authority exists; otherwise HOLD | T06 review evidence, merge not assumed |
| **T07** | Reporter implementation PR B and review | Declared parser dependency observed, sorted Decimal JSON/CLI implementation, new CI and independent review | T07 evidence; no auto merge |
| **T08** | Read-only V3.2 DELP + V3.5 cold entry + native RELAY comparison | Each runtime output recorded; any missing R3B→DELP call edge is **RED**; mismatches are not relabelled PASS | T08 cross-engine truth matrix |
| **T09** | Dry-run publisher, optionally scoped lab publication after authorized receipt | Dry-run **zero writes**; absent authorization apply stays denied; if scoped approval exists, same-source write/readback without human-text loss | T09 evidence of denied/approved cases separately |
| **T10** | Execute stress cases S01–S16, negative + positive controls | Every case has exact input/head/expected/observed/evidence/status; unknown/failed/forged data never grants acceptance | T10 case matrix, no blanket PASS |
| **T11** | Four independent cold entries: root, child, PR, repo only | Four separately sourced reconstructions, source-grade/UNKNOWNs and next action; compare to independent oracle | T11 4-result reconciliation |
| **T12** | Programme reconciliation | Precise PASS/FAIL/BLOCKED totals, source-to-surface trace and unresolved WP0/WP1 gaps; never upgrade #787 AC0/8 by claiming lab tests | Final `TASK_RESULT`, not programme certification |

### Exact first commands — T00

Run from the extracted project folder. Preserve a *sanitized* console log **per command** containing a literal `COMMAND=` and `EXIT_CODE=`; don't pipe away the actual exit status. The following is an example for one command; apply separately:

```bash
mkdir -p evidence/logs evidence/audit
bash -n scripts/bootstrap_lab.sh > evidence/logs/T00-bootstrap-syntax.log 2>&1
rc=$?; printf '\nCOMMAND=bash -n scripts/bootstrap_lab.sh\nEXIT_CODE=%s\n' "$rc" >> evidence/logs/T00-bootstrap-syntax.log
# Repeat for scripts/run_baseline.sh, python3 -m compileall,
# PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_harness*.py' -v
# PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_inventory*.py' -v
```

**Important:** re-read logs for leaked credentials and redact before saving/sharing. The expected application test exit is nonzero. Capture exact failing names and `NotImplementedError` evidence; unexpected errors are FAIL, not expected RED.

### Mandatory local audit ledger

After each task, append a digest-linked record using `scripts/audit_trail.py append`, for example:

```bash
python3 scripts/audit_trail.py append --ledger evidence/audit/events.jsonl \
  --task T00 --event TASK_EVIDENCE_DRAFTED --verdict PASS \
  --actor 'local-agent-session-001' --source-sha UNKNOWN \
  --artifact evidence/logs/T00-bootstrap-syntax.log \
  --note 'Readiness gate only; application still expected RED'
python3 scripts/audit_trail.py verify --ledger evidence/audit/events.jsonl
```

Before publishing, generate a draft via `scripts/task_evidence.py --task T00 --verdict PASS --operator ... --expected ... --observed ... --next ... --log evidence/logs/<command>.log --output evidence/T00-local.md` **only if the PASS-task logs you attach all have `EXIT_CODE=0`**. For a task containing intentional RED application tests, cite those logs as **additional** artifacts rather than PASS logs, and explicitly call out that failure in `--observed`. For expected-RED tasks, use `--verdict EXPECTED_RED` and a log with the expected nonzero exit. The generator does not prove GitHub observations or reviewer identity; you must include URLs and status by inspecting provider truth yourself.

Publish a separate durable comment to Common #875 after each task when authenticated `gh` is available:

```bash
gh issue comment 875 --repo reallaksh19/Common --body-file evidence/T00-local.md
# Then fetch/verify the actual new comment; DO NOT assume the last comment is yours.
gh api 'repos/reallaksh19/Common/issues/875/comments?per_page=100' \
  --jq '[.[] | {id,html_url,body}] | .[-3:]'  # use to locate ID; paginate as needed
python3 scripts/verify_github_comment.py --comment-id <REAL_ID> \
  --body-file evidence/T00-local.md --expected-author <GH_LOGIN>
```

**Readback must verify your exact draft marker and body SHA**. Do not treat the illustrative truncated `[-3:]` command as a sufficient guarantee when pagination exists; locate your specific comment ID/URL and read `gh api repos/reallaksh19/Common/issues/comments/<ID>`. Append `GITHUB_PUBLISHED` and `GITHUB_READBACK_VERIFIED` local audit records **only after** genuine provider observations, with issue-comment URL and a digest of the comment body. Do not paste an audit log containing secrets into GitHub. The authoritative task record is the verified comment in #875, not an editable local checklist.

For a task where `gh` access is absent: record `BLOCKED` or retain the draft locally, do not fabricate a GitHub URL or mark `GITHUB_READBACK_VERIFIED`. The next task requiring durable publication stays blocked.

## PAUSE / FAIL-CLOSED RULES

Stop immediately if: wrong repo owner, public lab, partial bootstrap, stale protocol SHA, failed graph validation, missing target PR head, unknown or failing actual CI, an attempt to credit FAILED facts, unqualified reviewer, unexpected GitHub writer permissions, or any potential mutation of Common production branches. Record and publish the safe blocker. A legitimate blocker is valuable test evidence.

## DELIVERABLES AFTER EACH TASK (REQUIRED)

1. `evidence/Tnn-local.md` (or split unit-level files for T04/T07) with fully checked/unchecked rubric.
2. `evidence/logs/<task>-<command>.log`, exact SHA256 and exit code.
3. `evidence/audit/events.jsonl` appended and verified, plus a record pointing at the exact GitHub comment if published.
4. GitHub issue/PR/Actions permalinks and exact material SHAs **only when provider-observed**.
5. One `TASK_EVIDENCE — Tnn` comment on Common #875 with readback proof, or explicit BLOCKED and a noninvented next step.
6. Updated `docs/CAMPAIGN_A_TASK_SCOREBOARD.md` **only as a disposable view**, never as the authority for claimed progress.

**DONE means** source-linked, reproducible task evidence exists for the exact material tested. Campaign A remains `V35_R14_E2E_NOT_QUALIFIED` until the actual missing programme join, WP0 independence and WP1–WP8 implementation are independently established. Do **not** assert FULL V3.5 prototype accepted from the synthetic lab.
