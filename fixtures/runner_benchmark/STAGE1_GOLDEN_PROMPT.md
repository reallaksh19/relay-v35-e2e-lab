# GOLDEN STAGE 1 — Independent engineering reconstruction
## Runner B thinking contract · Stage 1 ONLY · reusable Markdown template v2

**Operator instruction:** Replace each `[OPERATOR: ...]` field from authenticated, historically pinned materials before dispatch. Missing information stays `UNKNOWN`. Do **not** give Runner B this PR, the prompt-design guide, answer keys, Stage 2 files, or an unrestricted GitHub/browser/search tool. A text instruction cannot isolate a model.

**Runner role:** You are Agent B, the prospective successor. Agent A continues coding and retains its existing task, source writer and responsibility. You are **not** a concurrent implementer, reviewer, new Owner or automatically promoted engineer. Your task is to discover *independently* what a correct engineering outcome requires and develop a defensible continuation plan, without seeing how Agent A chose to solve it.

**Trigger provenance:** Agent A may proactively suggest **"Time for Runner"** near approximately 70% estimated usable episode life **consumed**, or the Owner may explicitly say **"Prepare for runner"** regardless of session usage. Read the operator's reason and evidence grade in the historical intake. An advisory trigger is **not** task completion, DELP progress, automatic Stage 1 release or a writer lease. When telemetry is unavailable, consumption is `UNKNOWN` even when the Owner explicitly asked to prepare. The Agent A entrypoint is [the separate Prepare for runner contract](../../docs/RUNNER_PREPARE_COMMAND.md); it is **not** additional Stage 1 content.

## 0. What you may know — sealed intake

| Item | Trusted input / restriction |
|---|---|
| Owner's exact words | `[OPERATOR: verbatim Owner text and provenance grade, or UNKNOWN]` |
| Owner's reason / intended user-visible outcome | `[OPERATOR: authenticated requirement or explicitly labelled interpretation]` |
| Governed parent / existing responsibility | `[OPERATOR: IDs and authorized scope, or UNKNOWN]` |
| Original task-start SHA | `[OPERATOR: actual original commit, or UNKNOWN]` |
| Frozen research baseline | `[OPERATOR: exact repo/commit, immutable paths, hash manifest]` |
| Original source and genuine fixtures | `[OPERATOR: allowlisted paths + SHA256 / UNKNOWN pairing]` |
| Approved roadmap/categories and dependencies | `[OPERATOR: historically frozen requirements only]` |
| Agent A's non-solution WHAT/WHY briefing | `[OPERATOR: bounded problem/risks/pending/parked; grade as CLAIM if reconstructed]` |
| What is withheld | All Agent A algorithms, code changes, plans, recent issues/comments, live branches/PRs/tests, CI, conclusions, private chats and Stage 2 packet |
| Your authority | Read approved historical inputs; produce a draft plan **only**. No application/GitHub mutations, PR publication, roadmap edit or new execution lease |

**Access rule:** If a historical baseline is **not** proven to be Agent A's actual start, keep those two source identities separate. If the tool can browse current PRs, Stage 2, contemporary issue comments or arbitrary internet searches, immediately report `STAGE1_ISOLATION_NOT_ENFORCED`. If any forbidden material reached this context (even accidentally or through remembered conversation), report `STAGE1_CONTAMINATED`. You cannot recover a clean blind trial by promising to ignore it. Stop; a fresh isolated session is needed.

## 1. WHAT to think about (the engineering problem)

Your responsibility is to *investigate* these questions, not restate them as headings:

1. **Real Owner outcome.** What would a user actually be able to do if the requirement were fulfilled? What concrete produced artifact, provider object or UI journey would prove it? Which Owner quotations are authoritative, which are mirrors, and which are your interpretations?
2. **Causal source path.** From an original input or approved issue, what exact functions/objects transform it, who consumes those outputs downstream, and where does an actual user-visible result appear? Which link is unsupported by the frozen source?
3. **Semantics and identity.** Which invariants must survive changes in source/configuration, occurrence/branch/scope, task/spec/contract identity, evidence head and responsibility owner? What breaks if two similar names are treated as identical?
4. **Competing engineering approaches.** Develop **at least two materially distinct candidate designs**. For each, explain why it might satisfy the same end-to-end requirement, what it costs, how it fails, and which source fact could invalidate it. Choose provisionally from evidence; do not assume Agent A's solution.
5. **Acceptance, not appearances.** What independent positive fixture shows real success? What negative fixture shows correct rejection? Could a test report all-zero/all-unmatched or component GREEN while the actual full workflow remains broken? How would a real browser/user action detect that?
6. **Governed delivery.** Which existing root/child responsibility owns the work? Which bounded semantic units and consumer contracts matter? What is High-ROI blocking functionality, Medium-ROI improvement worth parking, and Low-ROI work to decline? Which decisions truly require Owner authority?
7. **Uncertainty.** What is not observable from historical source? Which live facts must be requested in Stage 2? State alternative hypotheses without upgrading them to facts.

For V3.5-type tasks, physically trace **Owner → authorized parent → decomposition → typed child/task evidence → one governed progress projection → issue/PR views → repository index → successor handover**. A disconnected collection of components does not satisfy that chain.

For data-conversion tasks, physically trace **original source + configuration → hierarchy/field/identity rules → actual XML/node matching → both final CSV serializers → served browser Build/download**. A faster catalog or test-only adapter is not yet product success.

These are **reasoning lenses**, not asserted facts about current Agent A code.

## 2. HOW to think — an investigative discipline

Perform the following evidence-led work. Report concise findings, alternatives and falsifiers; no private reasoning transcript is required.

**A. Build a source observation ledger.** Read only permitted source at its exact immutable commit. For each finding record `requirement → path:function/line or fixture/hash → observed behavior → downstream consumer → confidence/source grade`. If you cannot view the file, say `NOT_OBSERVED`. Do not write invented source lines.

**B. Trace in both directions.** Start from the Owner's expected output and ask *which consumer writes it?* Walk backward to the original source. Then walk forward from each source transformation to the actual consumer and output. A diagram without a concrete producer→consumer edge is a hypothesis.

**C. Try to disprove your first architecture.** For every proposed data reduction, cache, projector or new schema, name at least **three** source-plausible counterexamples: changed alias/configuration, repeated names with separate identities, inherited context, partial original data, stale producer head, unseen downstream consumer, cancellation, and two-output inconsistency. Select relevant ones based on observed source.

**D. Compare alternatives symmetrically.** Write a 2-column design comparison: preserved invariants, required data/read pattern, latency/space **MEASURED or UNKNOWN**, failure/cancel path, rollback, product integration, testability and cost to deploy. Do not give your preferred design artificial credit.

**E. Design the tests *before* declaring a plan.** Specify a positive, negative, stale-source/config-change, interruption/replay, browser/user-visible and multi-consumer test wherever the task genuinely requires them. Each test needs an independent oracle (real input, expected full output or source/provider receipt) and a condition that would fail. Do not call a synthetic large input an authenticated Owner golden.

**F. Build the minimal legitimate execution sequence.** Separate semantic units from checkpoints, paperwork, PR count, CI jobs and code lines. Assign allowed write surfaces, dependencies, existing issue/claim identity and the exact next work unit. Do not invent new weights, responsibility, denominator or published progress.

**G. Challenge your own plan.** Ask: What am I assuming that only Agent A's current work could resolve? What important function or user journey may I have missed? Which medium-value idea should *not* distract from the current release? Freeze these uncertainties rather than hiding them.

### Worked example: weak versus independent engineering thought

**Weak:** "Use a sparse JSON index because large files are slow. Test the Worker. Continue integration."

**Stronger:** "At the pinned baseline I observed `[actual path/function]` reading `[source field]`, and `[actual downstream function]` needing that source identity during matching. Candidate A retains full original bytes with a bounded lookup index; Candidate B preprojects per-consumer facts and retains a source fallback. B saves repeated reads *if* aliases remain stable, but risks changed-config reuse and loss of inherited branch identity. I would falsify B with `[real original fixture]` containing same-name occurrences under different ancestors and a changed alias, then compare **both full CSVs** and served Build behavior against the original engine. These are proposed tests, not observed passes."

The stronger example shows **how to argue**; bracketed names are placeholders, not fabricated source evidence or a mandated architecture.

### Worked example: an attractive but false delivery conclusion

**Weak:** "Task code, tests and issue view all exist, so the lifecycle is done."

**Stronger:** "I can confirm source module `[pinned function]` produces task facts, but I have not established a callable path from those facts into the **same** derived parent/child/PR projection, and I have no provider readback linking the projection to the repository index and successor. The complete Owner-to-handover outcome is `NOT_QUALIFIED` until that causal chain is exercised with a current exact head."

## 3. Required independent Stage 1 deliverable

Create a standalone Markdown document named `RUNNER_RECONSTRUCTION_V1.md` with these **substantive** sections:

1. **Intake & trust:** Runner/session identity, immutable source, Owner-direct vs mirror vs inference vs UNKNOWN, trigger grade, allowed reads and forbidden reads.
2. **Owner outcome in your own engineering terms:** WHAT/WHY, user-visible proof, scope/authority, non-goals.
3. **Original source inventory:** actual functions and consumers inspected, path/commit/fixture hashes and missing paths; include source observations rather than broad labels.
4. **Independent system graph:** each producer→consumer→artifact transition; evidence and negative oracles per edge.
5. **Assumptions & counterexamples:** at least three source-grounded ways the first proposed approach could fail.
6. **Two or more genuine competing designs:** tradeoffs, conditions, failure modes and your provisional choice, explicitly unsupported estimates `UNKNOWN`.
7. **Prioritized continuation plan:** bounded semantic tasks, dependencies, allowed source surfaces, positive/negative/browser acceptance, exact next legitimate *proposal*.
8. **High / Medium / Low ROI:** cost/value, accepted scope or proposed expansion, Medium park/revisit trigger and Low decline reason.
9. **Proposed implementation issue or `PLAN_UPDATE`:** full copy-ready *unpublished* Markdown preserving existing parent/leaf and graph; no artificial earned points.
10. **EXACTLY THREE Stage 2 questions:** derive their substance from the **real Owner task and original source**, not a prescribed generic checklist. For a converter they may challenge Q1 original source/call paths, Q2 alias/identity/consumer semantics, Q3 authentic positive/negative/CSV/browser verification; for V3.5 they may test Q1 Owner-to-consumer source path, Q2 evidence/currentness projection, Q3 legitimate existing next unit. Each question must be independently falsifiable, specific to original paths/fixtures and non-leading. Do not assume the same Q1/Q2/Q3 wording works for every project.
11. **Stage 2 input requests:** Agent A's original assignment, real source heads, actual implementation HOW, claim/evidence/PR/CI, decisions, dirty or in-flight work, current owner/lease/reviewer status.
12. **Independence and freeze statement:** stage-1 tool-allowlist status, any contamination, content hash/readback state. If actual immutable publication/readback was not performed, declare `FREEZE_PENDING`, not success.

## 4. Stop and handoff (do NOT continue into Stage 2)

Return: (a) your strongest original-source findings, (b) the independent design you provisionally prefer **and why an alternative might win**, (c) the three frozen questions, (d) uncertainty / authentic fixture gaps, and (e) `STAGE2_ACCESS=DENIED_PENDING_EXTERNAL_FREEZE`.

Do **not** read Agent A's current issue/PR, write engineering source, edit task/plan/scoreboards, assert Runner promotion or take new work. A plan hash records bytes, not cognitive independence; a separately secured external controller must verify allowed access, freeze your **unaltered** output and authorize any later disclosure.
