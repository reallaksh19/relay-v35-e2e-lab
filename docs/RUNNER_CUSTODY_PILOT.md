# RNR-05 — LAB-only execution epoch and fencing controller

Scope: reallaksh19/relay-v35-e2e-lab issue #9, draft PR #10. No production V3.5, Common, Owner permission, reviewer, DELP evidence/currentness, GitHub live write or merge authority is created. The Stage 1 and Stage 2 functions remain unchanged.

## Implemented in the laboratory

- scripts/runner_custody.py implements a SQLite-backed single-host transaction gate for LAB-R1.
- Monotonic epoch: Agent A starts at epoch 1, promotion to B increments to 2. Rebootstrap and stale/duplicate promotions fail closed.
- HMAC-SHA256 transfer grant: binds responsibility, predecessor epoch and identity, successor identity and new capability hash, current candidate SHA, SHA256 of Stage 2 reconciliation, transfer ID and external operator receipt. Agent-authored reconciliation cannot sign its own grant.
- Stage 2 input must declare RUNNER_RECONCILIATION_V1, clean source, zero blockers, exact candidate and remote ref, and explicitly DENIED writer authorization. Still not independently authenticated Owner permission.
- Begin fencing: immediately stops all new old-agent write admissions; already admitted writes remain tracked.
- Complete promotion: refuses STARTED and UNKNOWN write operations, uncertain source oracle and moved candidate. Fresh provider observation must match signed candidate.
- Write admission: requires current agent, epoch, opaque capability, exact parser/test path, unique operation ID and trusted source oracle matching active SHA. This is ONLY broker admission, not a committed remote GitHub write.
- Already admitted successful write updates active candidate only with a new exact HEAD matching provider oracle; failure with ambiguous remote outcome cannot be marked definitive.
- SQLite BEGIN IMMEDIATE serializes transactions within a single trusted DB. No automatic expiration/reset or unsafe replay. Event rows are ordinary SQLite audit, not cryptographically tamper-proof.

## Critical safety limitation

This prototype does NOT enforce real GitHub custody. The Python class, signing key, SQLite DB, operator endpoints and trusted source oracle must be isolated in a separate controller runtime. Agents may only receive scoped admission endpoints and must not possess direct GitHub credentials, operator keys or DB access. Every actual mutation must be brokered with provider-side SHA compare-and-swap and readback. If an agent can bypass this gateway with a direct token, the single-writer guarantee is FALSE.

HMAC key proves possession of controller key, NOT identity or scope of the human Owner. operator_receipt is an opaque externally verified reference; the prototype cannot authenticate it.

## Proposed operator-only sequence

1. Operator securely initializes LAB-R1 for Agent A with starting SHA and secret capability, bootstrap receipt.
2. Runner B independently freezes Stage 1 plan; Stage 2 emits clean current-source read-only reconciliation.
3. Operator independently validates authority, issues a signed exact-HEAD+reconciliation+successor-capability transfer grant.
4. begin_fence changes state to FENCING. New A admissions fail; pending in-flight work must reach reconciled terminal outcomes.
5. finish_transfer requires no unresolved writes and matching trusted current-source SHA; atomically sets Agent B epoch 2. A old token/epoch is refused.
6. B can request brokered admission to the approved LAB-R1 paths only. A source change still requires provider CAS and verified readback.

## Native tests

    python -m py_compile scripts/runner_pilot.py scripts/runner_stage2.py scripts/runner_custody.py
    python -m unittest discover -s tests -p 'test_runner*.py' -v

24 new adversarial RNR-05 tests cover signed grant tampering, duplicate promotion, old token denial, source drift, uncommitted operation HOLD, uncertain provider result HOLD, wrong successor credential, competing transfers, parallel promotion on shared DB, scoped paths and audit events.

## Still open

No real GitHub API write adapter or external credential revocation; no authenticated operator service; no trusted provider source callback; no Runner B model or tool sandbox; no safe re-resolution of UNKNOWN operations; no live issue plan update/roadmap adaptation; no full V3.5 architectural acceptance or 50/70/85 comparative study. This is a broker state machine PROTOTYPE, not production authority. Preserve Common #864 WP0 hold, DELP canonicality, and the unmerged lab draft.
