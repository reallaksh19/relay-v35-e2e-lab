# RNR-06B2 — Distinct Unix principals and real ACL revocation (lab acceptance)

**Status:** privileged **local** acceptance test implemented and run. This is NOT real GitHub exclusive custody, Owner authority or production V3.5 adoption. Governing lab issue #9 / draft PR #10; Common #864 WP0 HOLD and #787 AC0/8 remain unchanged.

## Architectural defect corrected

The previous private broker accepted one fixed \`expected_client_uid\` for all writes, including after Agent A → Agent B promotion. Distinct executor identities could not work correctly: B would have been refused or would have had to reuse A's Unix identity. That was an execution-boundary defect, not something a prompt could fix.

The controller now accepts an **operator-provisioned** \`agent_uids\` mapping for Agent A and Agent B. It verifies the kernel-provided \`SO_PEERCRED\` UID against the agent claimed in each request, before write admission. The separately maintained RNR-05 capability and monotonic epoch still check authorization. Named identities cannot be selected by caller-controlled JSON alone. Shared agent UID and broker/agent UID are refused except via the explicit LAB-only unsafe test opt-in.

The executable service requires \`--client-uid\` for Agent A and \`--successor-client-uid\` for Agent B in \`github-lab\` mode. The single-UID compatibility path remains available only in the intentionally unsafe local test mode. Operator bootstrap, grant signing and promotion APIs remain *off* the agent-facing socket.

## Privileged real-UID laboratory oracle

\`tests/test_runner_cross_uid.py\` runs **only** on Linux as root when local user \`oai\`, user \`nobody\`, and \`libacl.so.1\` exist. Otherwise it SKIPS, which is **not** acceptance of OS credential isolation.

The test uses two real non-root Unix identities. A root-owned controller listens through a private AF_UNIX socket, and the operator grants precisely named filesystem ACL entries for traversal and connection. The test exercises genuine local bare-Git provider CAS:

1. B's UID cannot impersonate A even when given A's token; B's premature epoch is denied.
2. A's UID performs a real scoped commit using the broker, and the provider HEAD is read back.
3. Operator enters FENCING at that exact SHA: A can still reach the socket but is denied a new write.
4. Controller promotes B to epoch 2 after checking source and pending writes.
5. The operator revokes A's Unix socket/directory ACL while preserving B's ACL. A's connection then fails at the **operating-system permission layer**.
6. B's distinct UID uses B's new capability and epoch to commit to the next exact Git HEAD.

The operator's signing key, SQLite DB and Git remote are not opened by either agent subprocess; subprocesses are launched without inherited GitHub/SSH credential variables. This is **real local Unix identity + filesystem ACL evidence**, not a proof that GitHub remote credentials were revoked.

### Reproduce

Use a disposable, privileged Linux laboratory. Never run the test on an arbitrary production broker machine.

    python -m unittest discover -s tests -p 'test_runner_cross_uid.py' -v
    python -m unittest discover -s tests -p 'test_runner*.py' -v

Inspect the test result: **one passing cross-UID case is required** for the OS-boundary gate. A \`skipped\` case is NOT a cross-UID PASS. Ordinary hosted tests may still run as unprivileged users and must not imply that this gate was exercised.

## Provider governance observations, October 9, 2026

The linked GitHub connection could list repository rulesets and returned an **empty list**. The same connection was **forbidden (403)** when requesting branch protection details. Its effective read/write/admin capabilities do not establish that Agent A's other GitHub credentials, apps, browser sessions or workflow write permissions were revoked. Branch-level authorization remains **UNVERIFIED**, not automatically absent.

### Required before RNR-06B2 can qualify as REAL GitHub custody

- Independently provision the broker's own Unix service principal and an exclusive, minimally scoped GitHub writer credential. Do not reuse the ChatGPT connector's credentials or expose the broker identity to agents.
- Configure and verify exact filesystem ACL traversal/socket grants for the two permitted executor identities. Verify the operator's DB/signing key/SSH key remain private from both.
- Inventory and revoke ALL predecessor direct mutation paths (personal access tokens, deploy keys, GitHub apps, workflows, browsers and other sessions) or explicitly fence them through provider-enforced rules. Do not assume that broker-local denial prevents a direct push.
- Verify provider branch-level protection/rulesets via an authorized observer. Any API 403, missing rule or unverifiable permission makes the gate HOLD.
- Execute a real broker-initiated GitHub CAS write to a disposable LAB-only branch, re-fetch exact head, inject a conflicting writer, and prove an old Agent A direct attempt is denied. Do not perform this on main or V3.5 production.
- Authenticate Owner-approved grant and old-worker quiescence receipts using independent externally controlled authority. HMAC alone is only key possession; arbitrary receipt strings are not approval.
- Obtain actual hosted test step execution and an independent source-review verdict; earlier GitHub Actions runs ended before steps without assigned runners.
- Preserve DELP and canonical V3.5 authority; do not merge or issue live scoreboard updates from this lab.

**Disposition:** RNR-06B2 **local Unix identity and ACL mechanism verified**, while exclusive GitHub credential custody, browser/connector bypass exclusion, branch policy, and provider qualification remain BLOCKED. The draft PR is not mergeable on this evidence.
