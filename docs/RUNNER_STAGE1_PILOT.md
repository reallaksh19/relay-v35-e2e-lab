# RNR-01–03 Runner Stage 1 laboratory prototype

**Status: EXPERIMENTAL / LAB ONLY / NO AUTHORITY.**

Owner research concept: a successor begins preparation at approximately 70% of **estimated usable life consumed** (30% remaining) without seeing the primary's implementation. It reconstructs from original Owner intent, baseline, WHAT/WHY, pending/parked items, and golden fixtures; Stage 2 (not implemented by this PR) checks current source and reconciles against the predecessor's proposed plan.

Governed by [Common #787](https://github.com/reallaksh19/Common/issues/787), [#864](https://github.com/reallaksh19/Common/issues/864), [#878](https://github.com/reallaksh19/Common/issues/878), [lab #6](https://github.com/reallaksh19/relay-v35-e2e-lab/issues/6), and [lab runner issue #9](https://github.com/reallaksh19/relay-v35-e2e-lab/issues/9). This prototype is intentionally separate from Common production V3.5 and DELP. Do not count it as V3.5 AC1–AC8.

## Scope

- \`scripts/runner_pilot.py trigger\`: advisory, epoch-idempotent \`TIME_FOR_RUNNER_REQUESTED\` event; context percentage only when numeric usable-budget telemetry is supplied. The source is marked \`CALLER_PROVIDED\`, not authenticated. Unknown stays \`null\`. A named risk can trigger preparation before 70%. Never adds fields to \`CHECKPOINT_FACTS_V1\` or authors programme P/E.
- \`prepare\`: creates a *new* source-pinned, allowlisted Stage 1 directory **outside the code checkout**, reading files using \`git show <original SHA>:<allowlisted path>\`. No current working branch, PR statistics, current diffs, \`.git\`, or other files enter the bundle. The fixture is synthetic, not authenticated original private Owner chat.
- \`freeze\`: validates Stage 1 files/brief, checks the runner's independently written plan structure and 3 reconciliation questions, and writes a one-time digest receipt. \`verify\` detects subsequent edits. Hashes are integrity, **not principal identity or immutability under a hostile filesystem administrator**.
- **Not included:** live Runner B model launch, sandbox provisioning, Stage 2 planned/emergency reconciliation, lease/fencing, GitHub planning publication, automated scoreboards, performance superiority, independent reviewer verdict, merge or programme approval.

## Runtime isolation is a required external gate

The package builder is not itself an access-control boundary. For a real Stage 1 agent, place ONLY the allowlisted bundle in a separate, fresh sandbox/mount namespace with no implementation checkout, no GitHub or source-network access, no inherited credentials and no shared writable paths. Verify the sandbox restriction adversarially before asserting Stage 1 information independence. Do not use prompt-only prohibitions as proof.

The curated WHAT/WHY text must also be inspected for accidental descriptions of HOW Agent A solved the problem. Field allowlisting cannot enforce semantic non-contamination of human text.

## Reproducible example

Start from a local checkout of this lab at the pinned original source commit:

\`3392dc2147988492c54af2f1baa53aacd22fdcbe\`

1. Create an independent JSON briefing file \`/tmp/lab-brief.json\`:

\`\`\`json
{
  "schema": "RUNNER_WHAT_WHY_V1",
  "responsibility": "LAB-R1",
  "what": "Strict CSV input parsing and invalid-data rejection",
  "why": "Exact Decimal semantics and fail-closed validation",
  "claims": ["Agent A reports it addressed parser units U01/U02; these are unverified claims"],
  "pending": ["Check U03 against parent issue before execution"],
  "known_issues": ["Duplicate SKU, negative quantity, malformed headers, non-finite prices"],
  "parked": ["R2 reporting is a downstream responsibility"],
  "source_refs": ["docs/owner-intent.md", "fixtures/valid.csv"]
}
\`\`\`

2. Trigger the preparation request. This **does not** spawn or authorize a runner:

\`\`\`bash
python scripts/runner_pilot.py trigger \
  --epoch A001 --responsibility LAB-R1 \
  --state-dir /tmp/runner-trigger --used 7000 --budget 10000
\`\`\`

3. Build source-pinned Stage 1 material (destination must not exist and must be outside the working checkout):

\`\`\`bash
python scripts/runner_pilot.py prepare \
  --repo . \
  --commit 3392dc2147988492c54af2f1baa53aacd22fdcbe \
  --brief /tmp/lab-brief.json \
  --dest /tmp/runner-stage1
\`\`\`

4. In a separate sandbox, Runner B independently creates \`/tmp/runner-plan.json\` with exact keys \`schema=RUNNER_RECONSTRUCTION_V1\`, \`responsibility=LAB-R1\`, \`source_bundle_digest\` (SHA256 of the canonical \`runner_manifest.json\` object), \`purpose\`, \`next_actions\`, \`unknowns\`, \`stage2_questions\` (exactly three), \`parked_medium_roi\`. The independent plan must not include current PR or branch state.

5. Freeze/verify before granting Stage 2 live visibility:

\`\`\`bash
python scripts/runner_pilot.py freeze \
  --bundle /tmp/runner-stage1 --plan /tmp/runner-plan.json \
  --receipt /tmp/runner-plan-freeze.json
python scripts/runner_pilot.py verify \
  --bundle /tmp/runner-stage1 --plan /tmp/runner-plan.json \
  --receipt /tmp/runner-plan-freeze.json
\`\`\`

**WARNING:** \`/tmp\` is illustrative and not a sufficiently isolated production secret store. Enforce permissions/ownership and sandbox separation operationally.

## Tests and RED oracles

\`\`\`bash
python -m unittest discover -s tests -p 'test_runner_pilot.py' -v
\`\`\`

Cases test 70% threshold, unknown telemetry, early-risk trigger, duplicate idempotence, malformed metric/identity rejection, original-commit material (rather than current worktree), secret/PR-excluded file set, unapproved brief fields, foreign source refs, invalid original SHA, forbidden in-checkout bundles, modified source, surprise files, symlinks, plan tampering, and freeze structure.

The existing inventory-feature app workflow is deliberately RED until parser and reporter implementation. Do not classify that known application RED as a runner-pilot failure; use the dedicated native runner-pilot CI matrix for this scope.

## Pending implementation

**RNR-04:** Stage 2 reconciliation (with/without predecessor handover, exact branch/dirty worktree/CI/commit/source). **RNR-05:** genuine single-writer epoch/fencing and denial of old-agent direct writes. **RNR-06+:** governed plan publication, 50/70/85 comparative experiments, architectural V3.5 falsifiers. No promotion is implied by this PR.
