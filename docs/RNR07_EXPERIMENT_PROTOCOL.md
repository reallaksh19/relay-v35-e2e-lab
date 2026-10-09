# Runner thinking experiment — manual, evidence-led review protocol
## RNR-07 · Markdown-only · no simulator, no Python scoring and no YAML workflow

**Purpose:** Determine whether preparing an independent Runner around ~70% of Agent A's estimated usable episode life **consumed** produces a better, source-grounded continuation than a conventional handover, checkpoint, event summary or fresh cold reading. The optimum threshold and actual advantage are **UNKNOWN**.

**Agent A command entrypoint:** [Prepare for runner and proactive Time for Runner](RUNNER_PREPARE_COMMAND.md). Any perceived 70% threshold must be evidence-graded; explicit Owner preparation works even with UNKNOWN tokens. This file remains manual evaluation guidance, not a background trigger.

**This document is an operator/reviewer guide, not a model prompt.** Stage 1 Runner receives only the separately sanitized [Stage 1 prompt](../fixtures/runner_benchmark/STAGE1_GOLDEN_PROMPT.md) and original source packet. Stage 2 prompt, this guide, answers, and all predecessor-current evidence are forbidden until the external stage barrier is met.

## 1. The minimal experiment

Take a genuine, bounded engineering responsibility with real original Owner intent, frozen pre-work source, meaningful consumer/fixture goldens, current Agent A source and a previously stated acceptance goal. **Do not precompute the "right design."** Let an independent Runner investigate and propose it.

A useful comparison, if an external operator can independently run it:

| Condition | What the successor receives | Source/answer leakage policy |
|---|---|---|
| Cold GitHub | Original Owner scope, access to source at takeover | Current source available only at takeover |
| Terminal handover | Original intent + A's final packet | A claim remains unverified |
| Checkpoint | Original intent + approved durable checkpoints | Must verify current source |
| Event history | Original intent + authorized event log | Must verify current source |
| Runner ~50% | Sanitized historical Stage 1 at 50% consumed | Live A work withheld until sealed plan |
| Runner ~70% | Same historical Stage 1 at 70% consumed | Same barrier |
| Runner ~85% | Same historical Stage 1 at 85% consumed | Same barrier |

The "50/70/85%" levels require actual externally observed consumption data or must be marked **experimental approximate / telemetry UNKNOWN**. No created CSV slot or duplicated Markdown answer is an executed agent trial. Different arms must see **equivalent current source at the moment of comparison**; do not let an arm win by receiving more recent evidence.

Do not merely ask models for a summary. Give the same real objective and require a *different independent design, reasoned falsifier and genuine next-unit decision*. Then compare the proposals and their test outcomes.

## 2. How the OPERATOR must preserve independence

Before Stage 1, prepare only the allowed originals using [static packet formats](RUNNER_STATIC_PACKET_FORMATS.md). Use a genuinely new agent context. Physically limit repository/source and connected-app read access; disable ordinary GitHub PR/current-branch search and avoid sharing the current chat transcript. Run negative attempted-read checks if tools permit, and retain denial evidence outside the Runner context.

A statement like "I promise not to look" is **not** an isolation test. Neither a Markdown `Stage1` heading nor a plan SHA proves a clean context. If isolation is unavailable, label the resulting reasoning **RESEARCH_REHEARSAL / BLINDNESS_UNVERIFIED** and do not falsely claim an independent live study.

Runner writes only an external research response. Operator freezes its raw content, verifies exact immutable readback and keeps Q1/Q2/Q3 unchanged. Only after explicit Stage 2 read permission may Runner see A's actual plan, candidate code and latest provider observations. Production source writer admission is a different permission requiring fencing.

## 3. Manual adversarial case cards — test THINKING, not keyword matches

These are **reviewer-side examples**; do not include the expected answer in the fresh Stage 1 Runner packet. A better source-supported alternative is acceptable.

| Case / intervention | What a thoughtful Runner must investigate | Incorrect shortcut |
|---|---|---|
| Moving PR HEAD | Whether tests/evidence cover the latest candidate and its changed dependencies; how to requalify | Reuse old-green status |
| Missing downstream edge | Whether source facts physically reach the actual issue/PR/index or served XML/CSV user journey | Join green modules with prose |
| Owner amendment ambiguity | Original approved scope vs suggested change and human authorization; proposal vs accepted roadmap | Treat comment as Owner decision |
| Same-name source identities | Ancestor/branch/occurrence and configurable aliases; two genuine output paths | Whitelist fields by name |
| Attractive performance result | Compare *same* original task, complete output and authentic inputs; identify unmatched/negative XML | Declare a catalog microbenchmark a product release |
| Old executor crash | Durable provider observation, dirty/local UNKNOWN, in-flight write status and dual-actor fence | Pretend predecessor produced a final plan |
| Agent B's plan inferior | Admit A's stronger observed invariant/test, correct B's early hypothesis, park unnecessary redesign | Insist B's independent choice must be implemented |
| False progress claim | Single canonical evidence/projection basis, live issue/PR readback and stable responsibility | Publish independent P/E |
| Hosted CI pre-steps | Whether any runner actually executed command and at which SHA | Treat infra startup failure as source test RED or GREEN |
| UI-only or component-only proof | Authentic inputs, positive/negative oracles, actual full outputs, real browser action | Equate unit tests/screenshots with end-to-end qualification |
| Stage 1 source leak | Whether current A methods/PR comments were visible through tools, chat or fixtures; restart honestly | Pretend intentional nonuse cures exposure |
| Dual GitHub writers | Can A still mutate using any independent credential? Can B only act within new epoch/scope? | Regard a GitHub comment as revocation |

For each case, demand a **source citation, observation (or UNKNOWN), competing explanation, next falsifying test and legitimate decision**. A polished answer without original source path/function/fixture knowledge is not an engineering pass.

## 4. What a human reviewer should score

Use this worksheet for each *actual* independent session:

| Dimension | Questions to ask | Evidence grade |
|---|---|---|
| Original outcome | Does Runner preserve Owner exact purpose and user-visible deliverable? | SOURCE / MIRROR / INTERPRETATION / UNKNOWN |
| Depth of discovery | Did it inspect pinned source paths/functions and identify consumers? | OBSERVED / GENERIC / NOT_RUN |
| Alternative designs | Two materially different candidate methods and tradeoffs? | SUBSTANTIVE / SUPERFICIAL |
| Falsifiers | Three genuinely source-plausible failure cases and authentic positive/negative tests? | GROUNDED / UNSUPPORTED |
| Freeze and information firewall | Enforced read isolation and immutable plan, or merely self-report? | ATTESTED / CONTAMINATED / UNKNOWN |
| Four-view reconciliation | Owner, B, A, provider source compared including where B was wrong? | COMPLETE / PARTIAL / NOT_RUN |
| Scope/ROI | Verified High absorbed, missing High ordered, Medium parked with trigger, Low declined? | JUSTIFIED / PATCHWORK |
| Next unit | Exact existing governed responsibility, scope, tests and authorization? | ADMITTED / PROPOSED / HOLD |
| Real outcomes | Full provider/browser/consumer success with positive and negative goldens? | VERIFIED / NOT_QUALIFIED |
| Cost | Model input/output cost, time, rework, human corrections from external observations? | MEASURED / UNKNOWN |

**Use a vector of grades; do not compute a winner from unobserved telemetry.** The decision to adopt 70% as an optimization is valid only after matched independent sessions with meaningful outcomes, not because a hypothetical rubric chose it.

## 5. Honest release gates

- **PROMPT_DESIGNED:** two useful prompts, static input formats and worked reasoning examples exist. This is a Markdown deliverable.
- **CLEAN_STAGE1_OBSERVED:** independently attested tool/context boundary, actual Runner session and immutable plan; currently NOT ESTABLISHED by the documentation.
- **STAGE2_RECONCILIATION_OBSERVED:** Runner compared four perspectives, identified its own mistakes, and answered frozen Q1/Q2/Q3 against real source; requires real separate agent execution.
- **TAKEOVER_SAFE:** external authenticated old-writer revocation, pending-write settlement, new scoped epoch and provider verification; not implied by Stage 2.
- **VALUE_PROVEN:** independent trials outperform reasonable baselines at comparable task accuracy, cost and user-visible results; currently NOT ESTABLISHED.

No fixture creation, document review, local hash or CI badge can silently advance from the first grade to the others. Production Common and lab PR #10 security/custody remain separate; no Owner/Local merge or publisher rights are created by this research.
