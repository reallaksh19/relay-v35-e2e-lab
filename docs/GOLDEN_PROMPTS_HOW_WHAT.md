# Reasoning-first Runner — HOW to design the prompts; WHAT the agent must investigate
## Design rationale, source comparison and acceptance guide · Markdown-only revamp v2

**Scope:** research/prompt-design document for [lab PR #13](https://github.com/reallaksh19/relay-v35-e2e-lab/pull/13). It is **not** Stage 1 input, hidden test outcome, live acceptance, security/Owner approval, or a production V3.5 specification.

**The Owner's correction:** Supply **templates/formats and static input facts**, but make the *agent* do the difficult independent engineering work. Do not solve it with another Python script, generic YAML state machine, precomputed answer or a handover rephrasing tool.

**Reusable prompt artifacts:**
- [Stage 1 — independently reconstruct the engineering problem](../fixtures/runner_benchmark/STAGE1_GOLDEN_PROMPT.md)
- [Stage 2 — challenge both plans against actual source](../fixtures/runner_benchmark/STAGE2_GOLDEN_PROMPT.md)
- [Static input and output formats](RUNNER_STATIC_PACKET_FORMATS.md)
- [Manual falsifying cases / operator review](RNR07_EXPERIMENT_PROTOCOL.md)

## 1. What was learned from Common PRs #880, #881 and #882 — analyze, do not copy

These are **three different engineering examples**, not interchangeable prompt texts.

- [Common PR #880](https://github.com/reallaksh19/Common/pull/880) examines a real LFJ large-JSON / XML→CII recovery concern. Its most valuable idea is **source-function and original-fixture-grounded independent design**: seek actual consumer semantics, competing approaches, genuinely paired positive XML, two final CSV outputs, deployed browser journey and source-currentness. A 10MB synthetic/negative fixture or catalog benchmark cannot establish the authentic 30MB+ Owner outcome.
- [Common PR #881](https://github.com/reallaksh19/Common/pull/881) examines V3.2 Common #733 and R-PROJECTION. Its most valuable idea is **an agent honestly correcting its own Stage 1 assumptions** after seeing source—for example when a mandatory Owner-managed PR title was initially treated as optional. It also makes explicit that Stage 2 can produce a revised plan without acquiring a GitHub write lease.
- [Common PR #882](https://github.com/reallaksh19/Common/pull/882) is the merged V3.5 documentation-only reference. Its most valuable idea is to trace **the complete Owner→parent→decomposition→task evidence→sole DELP projection→live issue/PR→repository index→handover path** and distinguish the true Agent A start, frozen protocol reference and current candidate. Its real first Runner declared ambient-context contamination rather than claiming a clean Stage 1 trial.

**Cross-case conclusion:** a successful Runner is not the agent that writes the longest research memo, nor a machine that freezes a JSON schema. It is the agent that can find the **right original source and consumer paths, construct different possible solutions, produce falsifiable acceptance, correct its own errors and choose the next legitimate high-value unit**.

These files were independently synthesized; no Common golden fixture is copied into this lab PR. Retain Common PRs as **reference research**, and do not pass them as a whole repository tree to a supposedly blind Stage 1 model.

## 2. HOW I transformed the intended behavior into instructions

1. **Begin with the Owner's actual problem**, not Agent A's TODO list. Require an observed or provenance-graded original statement, explicit WHAT (observable completed behavior), and WHY (technical/user/business harm avoided).
2. **Give only static historical facts in Stage 1.** A pinned original commit, frozen scope/roadmap, source/fixture path list and honest Agent A WHAT/WHY claim permit genuine discovery. Live PRs and Agent A's coding HOW are not facts the Runner needs yet.
3. **Ask for a source *method*, not a fill-in-the-blank conclusion.** "Read caller and callee, walk data both directions, inspect original consumers, identify an invariant, challenge it with a concrete counterexample" is an actionable research sequence. "Explain the architecture" is not enough.
4. **Force competing designs, not a single favored solution.** Two materially different approaches and symmetric tests are mandatory. A decision is provisional until actual source facts can disprove alternatives. Estimates without measurements remain UNKNOWN.
5. **Build falsification into the first plan.** Positive/negative/golden/currentness/crash/browser cases should follow from Owner's use case. An all-unmatched parity check is not positive engineering match qualification; a passing component is not an integrated user result.
6. **Require typed provenance without replacing thought.** Tables for \`source line → observed behavior → consumer → assertion → falsifier\` force auditability. The table captures conclusions and concise justifications, **not private step-by-step chain of thought**.
7. **Force three *real* open questions.** Q1 investigates source path and consumer; Q2 material/current evidence; Q3 legal next unit and custody. They must be stored in the unaltered Stage 1 artifact, not composed with hindsight in Stage 2.
8. **Stage 2 is a new intellectual task.** Verify Agent A's disclosures; reopen actual frozen B plan; physically inspect candidate source/Owner graph/tests/browser; use a four-perspective matrix and identify when A is better, B is better or both missed a requirement.
9. **Treat ROI as an engineering choice rather than an activity list.** High-ROI already correctly completed work is absorbed rather than reimplemented; an unverified High claim requires proof; missing High within current scope is proposed for integration; Medium is parked with value/cost/reentry; Low is declined. New scope or weights require an Owner decision.
10. **Stop at the right boundary.** A brilliant reconciled plan can be useful even if old Agent A credentials remain active. The prompts do not authorize a write. The existing external security prototype is separate and unqualified for real GitHub custody.

## 3. WHAT good engineering thought looks like — five contrasts

### A. Follow the real output, not a fashionable optimization

**Insufficient:** "A sparse index reduces JSON cost."

**Better:** "Which original consumer fields, ancestor identity, configured aliases and two exported artifacts would break if the index dropped everything else? Read the pinned callers and serializers; propose lossless catalog vs consumer projection; design a real positive and negative output comparison before claiming savings."

The question creates a *research path*. It does not select the implementation for the Runner.

### B. Follow the whole delivery flow, not a scoreboard claim

**Insufficient:** "PR and issues have smart titles and evidence, so V3.5 works."

**Better:** "Can one exact task fact and accepted source basis be traced without substitution from Owner requirement through child issue, single DELP materialization, parent/PR title, repo-wise index and successor handover? Which physical call or readback is absent? Would changed-head evidence make all downstream claims stale?"

### C. Include a genuine opportunity for Agent A to be right

**Insufficient:** "My independent plan found an alternative. Implement it."

**Better:** "At the precise candidate, A already implements this invariant with an original golden and a changed-configuration negative. My candidate improves speculative memory use but loses source identity. ACCEPT_AGENT_A, document B's mistaken assumption, park the alternative unless authentic profile evidence reopens it."

This is *independence*, not contrarianism.

### D. Avoid making a lack of result look like a failed test

**Insufficient:** "Hosted CI says failure: application code is RED."

**Better:** "Runner name missing and zero steps: NOT_RUN_INFRASTRUCTURE. Tests have no execution verdict at this SHA. Neither copied GREEN from an older head nor code RED is justified; qualify the actual exact head before promotion or release."

### E. Name the next legitimate unit, not every possible task

**Insufficient:** "Add a dashboard, improve docs, rewrite the pipeline and scale to 90MB."

**Better:** "The first missing physically connected dependency is \`[producer→consumer]\`; existing responsibility \`[ID]\` owns it and its acceptance. Proposed bounded unit: \`[one outcome]\` plus golden/changed-head/browser tests. Park optional dashboard and 90MB tuning pending authentic fixtures. Do not create a replacement responsibility because the executor changed."

## 4. Minimal quality contracts

| Dimension | The Runner must actually demonstrate | False positive to reject |
|---|---|---|
| Owner intent | Direct/mirror/paraphrase/UNKNOWN labels and real user-visible objective | Treating mutable title as Owner authority |
| Independent source reading | Pinned path/function/consumer and original fixture observations | Generic architectural prose |
| Thinking depth | Two alternatives, symmetric tradeoffs, three falsifiers, provisional choice | Copying a favored solution |
| End-to-end semantics | Positive and negative cases and the actual output path | Unit test or empty-output parity alone |
| Original Stage 1 | Source-bounded plan, 3 strong questions, ROI, exact immutable receipt | A hash passed off as access isolation |
| Stage 2 intelligence | B vs A vs source vs Owner, including B's own mistakes | Agreeing with the predecessor |
| Delivery governance | Same parent/leaf, existing programme progress authority | Extra child/weights/P/E for Runner |
| Writer safety | Explicit independent external takeover proof or HOLD | GitHub comment = revocation |
| Claim honesty | Observed/executed/source-authenticated vs UNKNOWN | Fake provider tokens, telemetry or review |
| Value | A justified High-ROI next unit and parked Medium alternative | Long checklist without decisions |

## 5. Why no new runtime code belongs in this PR

Python can compare hashes or score static fixture keywords. It **cannot** by itself prove that a new model genuinely investigated original source, understood the Owner's outcome, found a better plan, exercised an actual Chromium journey, or had no prior exposure. Encoding expected answers into the same source tree may *reduce* independence.

Likewise, a YAML stage transition is not a cognitive method and does not grant safe GitHub credentials. A real externally trusted orchestrator is a separate deployment project. For the requested prompt study, the useful assets are **human-readable operator restrictions, the two Markdown prompts, static intake/reality formats, worked counterexamples and a reviewer rubric**. Any future automation should implement those proven boundaries rather than define the architecture by accident.

## 6. Review and decision boundary

A prompt review may conclude:
- **FORM_PRESENT:** necessary substantive questions, output, negative examples and source fields are present.
- **ENGINEERING_INSIGHT_OBSERVED:** a genuinely independent agent produced new evidence-grounded alternatives and later corrected them against actual source.
- **CLEAN_STAGE1_VERIFIED:** an external controller attested actual enforced tools/context restriction and immutable plan; not achievable merely by this Markdown PR.
- **STAGE2_RECONCILED:** the separate admitted Runner answered original frozen questions and made real source-backed decisions.
- **SAFE_CONTINUATION_VERIFIED:** only after separately authorized exclusive custody and work that passed its real evidence/browser oracles.

The first is a document quality result; the others require real execution and external evidence. **A 70% trigger optimum is UNKNOWN** until controlled independent sessions are compared against other approaches.
