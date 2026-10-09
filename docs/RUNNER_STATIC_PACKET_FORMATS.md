# Runner static intake and reality formats — operator fillable Markdown v2

**Audience:** External experiment operator / Owner. **Only the completed Stage 1 intake** should be visible to a clean Stage 1 Runner. This document, the Stage 2 template and evaluator examples must be stored separately from that Runner's readable environment.

**Agent A entrypoint:** when the Owner says **"Prepare for runner"**, use [the preparation command](RUNNER_PREPARE_COMMAND.md). At checkpoints, consult the same document for a provenance-graded **"Time for Runner"** recommendation near 70% estimated working-life consumption. This document stores sanitized original facts; it does not read telemetry or auto-start B.

**This file is a format, not a tool permission system.** An operator must actually enforce source, context, tool, network, role and writer boundaries. If that is not possible, stage independence = NOT VERIFIED. Do not put current Agent A paths, PR numbers, implementation HOW or Stage 2 facts into the Stage 1 packet.

## Template A — Stage 1 original-intent/source intake (copy *only this section* into the Runner workspace)

**INTAKE_ID:** `[operator-generated opaque id]`  
**RESPONSIBILITY_ID:** `[existing authorized parent/leaf or UNKNOWN]`  
**AGENT_A_STATUS:** `CONTINUES_AS_PRIMARY`  
**RUNNER_AUTHORITY:** `RESEARCH_READ_ONLY`  
**TRIGGER_REASON:** `[OPERATOR: EXPLICIT_OWNER_PREPARE / APPROX_70_PERCENT / EARLY_CONTEXT_RISK / UNKNOWN]`  
**LIFE_CONSUMED:** `[OPERATOR: percentage only with verified used+usable denominator; otherwise band or UNKNOWN]`  
**METRIC_SOURCE:** `[OPERATOR: PROVIDER_MEASURED / OPERATOR_EPISODE_PROXY / AGENT_RISK_OBSERVED / UNKNOWN]`  
**METRIC_CONFIDENCE:** `[OPERATOR: HIGH / MEDIUM / LOW / UNKNOWN]`  
**OBSERVATION_REF:** `[OPERATOR: timestamp + external source receipt, or NOT_AVAILABLE]`  
**SOURCE_CUTOFF:** `[historical cutoff timestamp; original session start separately UNKNOWN if not proven]`

### Owner purpose — preserve source grade

> `[verbatim Owner words, if authenticated; otherwise cite GitHub mirror as MIRROR and say original direct source UNKNOWN]`

**Owner WHAT:** `[observable outcome; separate from agent paraphrase]`

**Owner WHY:** `[actual harm/cost/quality defect and what must remain invariant]`

**Current approved responsibility and non-goals at historical cutoff:** `[scope, graph, dependencies, parked items; cite frozen permitted source]`

### Original repository and fixtures

| Field | Exact source / unknown | Why Runner may read it |
|---|---|---|
| Source repository and immutable baseline | `[repo@40-character-commit]` | Historical source observation |
| True Agent A task start | `[commit or UNKNOWN]` | Preserve provenance distinction |
| Approved path allowlist | `[path@SHA for every module + direct import rule]` | Source/function/consumer discovery |
| Owner issues/roadmap snapshot | `[curated immutable excerpt + source grade]` | Original purpose and scope, not live progress |
| Genuine positive fixtures | `[original file path + SHA256 + positive suitability VERIFIED/UNKNOWN]` | Real user-output oracle |
| Genuine negative fixtures | `[original file path + SHA256 + negative suitability VERIFIED/UNKNOWN]` | Ambiguity, no-match, stale and error cases |
| Source-size / cost numbers | `[actually observed metric source or UNKNOWN]` | Distinguish measured from aspiration |

### Bounded Agent A WHAT/WHY briefing (not an implementation disclosure)

**Originally assigned problem:** `[symptom, acceptance, unchanged requirements]`

**Known open risks:** `[failure risks phrased as questions; NOT how A fixed them]`

**High-priority obligations:** `[outcomes whose completion is unknown]`

**Medium-priority parked:** `[ideas + why optional + return trigger]`

**Still UNKNOWN:** `[source/functions/consumer pairing, data equivalence, approval, negative oracles]`

**No current-status claims:** The packet does not include contemporary HEAD, PR numbers, CI, Agent A diffs/tests, current plan or progress/title/scoreboard values.

### Stage 1 trigger provenance and tool admission (operator side only)

A reason code reflects **why preparation was requested**, not proof of exact consumption. If the Owner invoked "Prepare for runner", use `EXPLICIT_OWNER_PREPARE` regardless of usage; do not fill in `~70%` by convention. Stage 1 Runner receives no Agent A implementation HOW or live PR/coding telemetry. The trigger is advisory and gives no writing authority.

### Stage 1 technical admission (operator side only, not a model assertion)

- [ ] Runner B session actually new and not already exposed to A's implementation.
- [ ] Only immutable approved source and curated intake are readable; no unrestricted connector/search/browser or shared conversation history.
- [ ] Forbidden source/Stage 2 attempted reads would be denied and logged.
- [ ] No current code, issue-comments feed or evaluator expected answer leaks through helper instructions, prompts, mounted files or source manifests.
- [ ] Runner output is limited to an external controlled research artifact; engineering source/GitHub issue edits are unavailable.
- [ ] If any item is unverified, no clean Stage 1 certification.

**Runner task:** Supply the separate [Stage 1 thinking prompt](../fixtures/runner_benchmark/STAGE1_GOLDEN_PROMPT.md), not a precomputed recommended architecture.

---

## Template B — After freeze: Stage 2 Agent A reality intake (**never expose before Stage 2 read admission**)

**REALITY_PACKET_ID:** `[operator id/version]`  
**MODE:** `PLANNED_HANDOVER / INTERRUPTED_NO_PACKET`  
**STAGE1_FREEZE_REF:** `[Runner B original plan immutable URL/content hash/readback]`  
**STAGE1_ACCESS_ATTESTATION:** `[external read enforcement receipt or NOT_VERIFIED]`  
**STAGE2_DISCLOSURE_APPROVAL:** `[actual Owner/coordinator authorization or UNKNOWN]`

| Material | Agent A claim/record | Independent provider/source observation |
|---|---|---|
| Original Owner assignment and actual start | `[A report/UNKNOWN]` | `[direct source or mirror, SHA, grade]` |
| Original plan and accepted amendments | `[version/ref]` | `[authorized revision, graph, unchanged denominator]` |
| Current repo, branch, candidate HEAD | `[A claim]` | `[exact latest ref readback/time]` |
| Changed files, functions and downstream consumers | `[A list]` | `[independent source diff/call path]` |
| Completed semantic outcomes | `[A evidence claims]` | `[current exact material, tests, provider/browser]` |
| Unfinished/failed approaches and negative goldens | `[A report]` | `[code, failing cases, authentic source]` |
| Real user journey / dual output / live issue index | `[A report]` | `[Chrome/provider readback or NOT_RUN]` |
| High ROI missing / Medium ROI parked | `[A priorities]` | `[Owner scope/source impact; evaluate, do not copy]` |
| Open GitHub writes / dirty worktree | `[A report or unavailable]` | `[controller/provider state; UNKNOWN where absent]` |
| Current executor, lease and protected paths | `[A report]` | `[independent authority readback]` |
| Proposed next engineering unit | `[A preference]` | `[current existing responsibility + accepted scope]` |

**Historical packet caution:** Agent A's snapshot may be correct *when created* but stale today. A packet is evidence about A's view, not an active current-source verdict. A missing/crashed Agent A must be marked `INTERRUPTED_NO_PACKET`; do not invent words on its behalf.

### Stage 2 external read-admission receipt

Record separately: original Runner B artifact and content digest, immutable stage1 source/input manifest and read audit, contamination grade, owner/controller read approval, Stage 2 packet digest, Stage 2 read scope, and `EXECUTOR_PROMOTION=NONE`. An unsigned agent-authored assertion cannot satisfy any external control.

### Distinct future promotion receipt (separate from Stage 2 plan)

Evidence must answer: Is A's old write credential/lease *actually* revoked? Are all in-flight operations settled? Does provider HEAD still equal the approved reconciled candidate? Is B newly authorized for **one existing responsibility** with an exclusive epoch and bounded source paths? Is the Owner/Local reviewer/merge gate distinct and intact? Until independently verified: `HOLD_DUAL_WRITER_RISK`, **no coding or GitHub publication**.

---

## Template C — Reviewer scorecard (evaluator only)

Do not show the following expectations to Stage 1 Runner B.

| Axis | Observable minimum | Result |
|---|---|---|
| A. Independent engineering comprehension | Original path/symbols, actual consumers, two alternatives, three falsifiers, meaningful positive/negative acceptance | PASS / FAIL / NOT_OBSERVED |
| B. Enforced original-source blindness | New independent context, technical read allowlist, denied forbidden reads, no premature A HOW | ENFORCED / CONTAMINATED / UNKNOWN |
| C. Frozen answer integrity | Exact raw response digest, immutable source/readback and unchanged three questions | VERIFIED / NOT_VERIFIED |
| D. Four-way reality reconciliation | Original Owner vs B vs Agent A vs current provider source; explicit A-better, B-better, both-wrong or UNKNOWN examples | OBSERVED / INCOMPLETE / NOT_RUN |
| E. Correct next-unit/ROI choice | Verified High absorbed, missing High ordered, Medium parked with trigger, existing responsibility preserved | GROUNDED / UNSUPPORTED |
| F. Safe custody and external authority | No dual writer, no Owner/reviewer impersonation, source recheck and epoch after fencing | PROVEN / HOLD / NOT_RUN |
| G. Actual downstream outcome | Full authentic source/golden consumer chain and real browser/provider readback when relevant | QUALIFIED / NOT_QUALIFIED |
| H. Comparative value | Comparable real Runner vs cold/handover/checkpoint sessions, external cost/error measurements | OBSERVED / NOT_RUN |

**A clean-looking written plan earns no B/F/G/H PASS automatically.** A prompt should motivate genuine research, not award it credit.

## Optional case profiles for OPERATOR reference (never part of an unfiltered Stage 1 workspace)

- **LFJ/Resolver research (Common PR #880):** source-case baseline `3D_Converters@1205639a43e9ce1589360479d2558678aebcfab7`. Historical original JSON examples include 733,806-byte `Benchmarks/1885Sjson/Sjson.json` and 10,232,634-byte `Benchmarks/1885_NC/1885_NC.json`. Authentic XML positive-pair suitability must be independently established; synthetic 30MB is not authenticated 30MB.
- **Common V3.2 R-PROJECTION (Common PR #881):** case baseline `Common@80a9c03d8f33ace129d21cb868c93e9359a8868a`, historical governed #718 / responsibility #733. The Runner should independently discover mandatory Owner-managed title/PR requirements, not assume optional functionality.
- **Common V3.5 whole lifecycle (Common PR #882):** source reference `Common@13989969f6b7e432c4f7c1ddfe975449dba53593` is a *protocol reference*, not a verified Agent A starting commit. Original end-state: a physically connected Owner→parent→child→evidence→one DELP→issue/PR→repo index→handover chain. First historical Stage 1 disclosure was **CONTAMINATED by ambient context risk**, not a certified fresh blind run.

These facts help an operator prepare distinct **source-pinned packets**. They must not be mixed into a model's blinded workspace when outside its authorized original-source envelope.
