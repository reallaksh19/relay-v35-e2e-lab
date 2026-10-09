# Prepare for runner — Agent A command and proactive suggestion contract
## Markdown-only invocation · session-life evidence · sanitized Stage 1 handoff

**Purpose.** Make the exact Owner prompt **"Prepare for runner"** useful in any engineering session where the coding agent has explicitly loaded this document. Also instruct Agent A to **suggest** **"Time for Runner"** near the working-life threshold, without waiting for Owner to notice context exhaustion.

**This is a human/agent operating instruction, NOT a ChatGPT built-in command, persistent timer, installed Common protocol, provider telemetry collector, automatic agent spawn, or authority to update issues.** A model cannot read its true context budget unless an authorized runtime exposes it. These instructions are candidate lab material in draft PR #13; production Common V3.5 and the separate single-writer gate remain unchanged.

## A. Exact invocations — what the coding agent should do

### Owner writes: "Prepare for runner"

Treat this as a **manual preparation command** even if context-life usage is below 70%, unknown, or the current task is incomplete. Do not ask the Owner to restate known repository, current issue, plan or accepted scope.

1. **Stay Agent A**: finish no hidden merge, do not withdraw from coding or surrender writer rights. Identify current repo/responsibility and accepted source/protocol/Owner plan. Confirm what you know; mark what is missing.
2. **Collect the best available session-life evidence** as described below. The Owner command is itself a sufficient preparation trigger: do not manufacture a 70% metric as justification.
3. **Read original-source facts and separate trust grades.** Find the true original task-start commit if provable; otherwise distinguish original historical source, initial assignment, present HEAD and any protocol reference. Preserve original Owner WHAT/WHY, approved responsibility, roadmap, known High/Medium work, original fixtures and baseline source *without* disclosing Agent A's chosen algorithms.
4. **Produce a Stage 1 sanitized packet** using Template A in [RUNNER_STATIC_PACKET_FORMATS.md](RUNNER_STATIC_PACKET_FORMATS.md), plus the original source/fixture allowlist and [Stage 1 thinking instructions](../fixtures/runner_benchmark/STAGE1_GOLDEN_PROMPT.md). Ask an external operator to verify the source cutoff and actual read isolation. **Do not put current PRs, source diffs, plan changes, test results or Agent A code/approach into the Stage 1 packet.**
5. **Separately prepare a Stage 2 reality packet** using Template B in [RUNNER_STATIC_PACKET_FORMATS.md](RUNNER_STATIC_PACKET_FORMATS.md): current HEAD/PR, actual HOW, changed source consumers, tests and evidence with exact tested SHA, defects, Owner decisions, open operations, pending High and parked Medium work. **Do not expose this packet or even its paths to the Stage 1 Runner.** If the current agent/conversation has no separate protected location, retain only a local operator draft and state _STAGE2_STORAGE_NOT_ISOLATED_; do not transmit it to B.
6. **Report readiness honestly**: source packet completeness, missing original source/fixture hashes, current life-estimate confidence, Stage 1 access enforcement state, whether a fresh B context has actually been started, and next safe Owner/operator action. A research packet is not a frozen independent Runner plan.
7. **Continue the existing engineering task** unless the Owner separately orders a pause or authenticated controller demonstrates a valid execution handoff.

### Agent A should suggest: "Time for Runner"

At a normal semantic-unit boundary, checkpoint, notable research pivot, or significant interruption warning, inspect **available evidence** of remaining usable working life. When a threshold or serious early-risk condition is met, make one concise recommendation:

> **Time for Runner.** My estimated usable session life is **[value or UNKNOWN]** consumed (**[source and confidence]**). I recommend preparing an independent Stage 1 Runner now while I continue the current responsibility. If you say **"Prepare for runner"**, I will assemble the sanitized original WHAT/WHY/source packet and keep my current implementation private until a separate Stage 1 freeze. This suggestion gives Runner B **no write authority**.

If the Owner already said **"Prepare for runner"**, immediately perform preparation; do not merely repeat the suggestion. A once-per-episode, per-responsibility recommendation is enough; repeat only when meaningful status changes or Owner asks.

## B. Which statistics to inspect — and which NOT to use as context-life

| Signal | Permitted evidence source | How to interpret |
|---|---|---|
| **Used / usable context tokens** | Explicit provider/orchestrator telemetry for **the same ongoing Agent A session** with known usable budget | If both trustworthy, life consumed = used / usable × 100, with source, observation timestamp and grade. Never infer the denominator from a model name or plan. |
| **Episode or turn budget proxy** | Operator-configured working-episode time/turn allocation and observed elapsed episode turns/time; checkpoint timing can support the risk assessment but completed semantic units are NOT token consumption | Estimate a **band**, not a precise 70.00%. Identify proxy assumptions and confidence. |
| **Early degradation / interruption warnings** | Observable compaction/context-loss indicator, repeated information reloads, incompatible source-head reconstruction, long dependency research, tool/agent restarts or impending large semantic unit | May prompt early advisory even with context percentage UNKNOWN. Explain the observed risk, not a fabricated percent. |
| **Work difficulty** | Remaining High-ROI units and next critical task's expected context/research needs | Supports scheduling a read-only successor early; cannot itself measure consumed tokens. |
| **V3.5 agent health** | Seven existing health dimensions: materialization, evidence, checkpoint distance, size, base drift, interruptions, liveness | Independent health signal, **not** context-life percent. A red/unknown dimension may justify investigation; it does not imply 70% consumed. |
| **DELP/P/E, commits, CI, issue title, code lines** | Progress/project state | **NOT** life consumed. Never equate 70% task completion, issue weight or number of PRs with the Runner trigger. |

**Provenance tags:** `PROVIDER_MEASURED`, `OPERATOR_EPISODE_PROXY`, `AGENT_RISK_OBSERVED`, `UNKNOWN`. Add timestamp/session ID when actually available. `CALLER_PROVIDED` is not equivalent to provider-authenticated telemetry.

**Recommendation bands (advisory, not automatic commands):**
- **Below 65%**, with credible direct telemetry and no important risk: continue normally; keep original/Owner notes durable at ordinary checkpoints.
- **Approximately 65–75% consumed**: suggest **Time for Runner** proactively near 70%; do not claim that precisely 70.0 is optimal.
- **Above 75% or strong early loss/compaction risk**: recommend immediate preparation if still possible; distinguish late preparation from successful early trigger.
- **UNKNOWN** consumed, no material risk: report no measured threshold; do not nag the Owner or infer capacity.
- **UNKNOWN** consumed, with concrete material risk: suggest early **Time for Runner** explicitly based on **risk**, not a false metric.
- **Explicit Owner command**: prepare now, irrespective of number or risk.

This is a trigger suggestion, **not** an automatic Runner launch or transfer. Provider-life telemetry might be absent; then describe the basis as a proxy/risk or UNKNOWN.

### Worked examples — correct and incorrect use of statistics

**Example 1: direct telemetry.** Operator reports 70,000 used out of 100,000 usable context tokens for **the same session** at an identified checkpoint. Life consumed = 70%. Agent A may say: *"Time for Runner — 70% measured from operator telemetry at [checkpoint]; I propose independent Stage 1 preparation."* These figures are **illustrative**, not current-session facts.

**Example 2: partial token data.** A tool reports 70,000 tokens processed but gives no usable window denominator or indicates some tokens belong to earlier sessions. **Wrong:** "70% consumed." **Right:** "Usable episode life is UNKNOWN; I cannot derive 70% from these counts."

**Example 3: no telemetry, real risk.** A long LFJ source investigation has been repeatedly interrupted and the next bounded unit requires inspecting consumer matching, both CSVs and Chromium. **Right:** "Time for Runner suggested **early due to observed research/interrupt risk**, context consumption UNKNOWN; Agent A continues. Prepare original-source-only intake."

**Example 4: explicit Owner instruction at 30% or UNKNOWN.** Owner says "Prepare for runner." **Right:** Immediately create a sanitized input draft and separate current-state reality draft, while keeping the normal primary coding task; **do not insist on meeting the 70% threshold first**.

**Example 5: incorrect metric substitution.** DELP parent P70/E60 or seven health components at ADVISORY are *not* episode life consumed. **Wrong:** "Task is 70% done; Runner threshold reached."

## C. Suggested Agent A response format (compact and useful)

When a threshold suggestion is warranted, give one short paragraph:

**Time for Runner — recommended [MEASURED / ESTIMATED / RISK-BASED].** The available working-life signal is **[source+observed value+confidence / UNKNOWN]**. Reason for recommendation: **[specific evidence of proximity or risk]**. Agent A retains current coding. Say **"Prepare for runner"** to create the historical WHAT/WHY/source-only packet; no Stage 2 release or writer transfer is implied.

After the Owner actually commands preparation, provide this checklist:

- [ ] Original Owner intent and approved scope identified with source grade.
- [ ] True Agent A start vs historical protocol/source baseline distinguished.
- [ ] Original source/fixture allowlist and authentic positive/negative pairing reviewed; missing inputs UNKNOWN.
- [ ] High-ROI outcomes and Medium-ROI parked ideas described **without implementation HOW**.
- [ ] Stage 1 packet drafted and kept free of current A PR/code/evidence.
- [ ] Stage 2 reality draft prepared **separately and not exposed**.
- [ ] Real Stage 1 technical read isolation verified by external operator (else NOT_VERIFIED).
- [ ] Fresh Runner B actually started (else NOT_STARTED).
- [ ] Runner B independent Stage 1 plan authored/frozen/read back (else NOT_FROZEN).
- [ ] Old A writer remains active; B has no production write permission.

Finish with **`PREPARED_INPUT_ONLY` / `STAGE1_ISOLATION_PENDING` / `STAGE1_READY_FOR_EXTERNAL_OPERATOR`**, selecting only the evidenced state. Never return "Runner B is ready to code" from packet drafting.

## D. How this ties to the two golden prompts

`Prepare for runner` does **not** make Agent A author Runner B's answer. It prepares the input envelope and asks a separately isolated B to undertake the substantive investigation defined in [Stage 1](../fixtures/runner_benchmark/STAGE1_GOLDEN_PROMPT.md): original code/consumer discovery, competing approaches, counterexamples, positive/negative tests, High-ROI and parked Medium decisions, three domain-specific questions, immutable independent plan.

Only after that plan is externally frozen, a trusted operator may give B the privately held Agent A reality packet and [Stage 2 thinking instructions](../fixtures/runner_benchmark/STAGE2_GOLDEN_PROMPT.md). B then compares **Owner intent, frozen B beliefs, A claims and live source**—and may find either agent wrong. A separate controller handles possible future execution authority; the instruction cannot revoke live GitHub credentials.

## E. Installation truth

- **Implemented here:** Markdown instructions, manually invokable prompt phrase, evidence grading, threshold recommendation, static packet preparation rules and cross-links to Stage 1/2 documents.
- **Not implemented by this document:** session-token telemetry API, scheduled/background checks, agent auto-spawn, secured browser/connector sandbox, immutable plan publishing, authenticated Owner approval, real GitHub epoch fencing, integration into every Common V3.5 agent's automatically loaded coding instructions.
- To make "Prepare for runner" **universally discoverable**, the Owner must separately approve a concise reference to this contract in the actual engineering-agent entrypoint/accepted Common skill or per-agent prompt. Until then an agent follows it only after it has been given or has read this file. Do not announce global wiring or a measured 70% trigger from the mere existence of this Markdown.
