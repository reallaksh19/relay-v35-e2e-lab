# RNR-06 — Git ref CAS provider pilot, NOT a deployed credential gateway

Scope: [lab issue #9](https://github.com/reallaksh19/relay-v35-e2e-lab/issues/9), [draft PR #10](https://github.com/reallaksh19/relay-v35-e2e-lab/pull/10). Common V3.5, DELP, programme acceptance, Writer OFF, issue/PR title publication, Owner/Local merge authority unchanged.

## Bounded implementation

- scripts/runner_provider.py: GitRefProvider and BrokeredGitWriter. A trusted controller pins the Git remote and dedicated laboratory branch; no runner may choose a remote. Production transport accepted only for reallaksh19/relay-v35-e2e-lab over SSH. Local bare-directory transport is permitted only in explicit test mode.
- On an admitted LAB-R1 write: verify actual remote HEAD; create a one-file change and Git commit from exactly that remote parent in a temporary bare object store. Only parser and parser-test paths are permitted; R2 reporter is denied.
- Persist a durable operation-intent row (id, candidate commit SHA, digest, branch) BEFORE dispatching a remote push.
- Use a real Git compare-and-swap push: git push --force-with-lease=refs/heads/BRANCH:OLD_SHA REMOTE NEW_SHA:refs/heads/BRANCH. The push rejects racing updates. Verify the observed provider HEAD equals the intended candidate before finishing SUCCEEDED.
- Any timeout, ambiguous outcome or competing ref change leaves the operation UNKNOWN and holds subsequent writes and promotion. Never retry a potentially applied commit.
- Operator-only resolve_unknown: compare a persisted intended SHA and provider readback; require externally verified full worker quiescence before classifying new-head success or old-head failure. Third-party HEAD remains HOLD.
- sqlite3 BEGIN IMMEDIATE and scoped epoch controls from RNR-05 remain in effect.

## Local tests

    python -m py_compile scripts/runner_custody.py scripts/runner_provider.py tests/test_runner_provider.py
    python -m unittest discover -s tests -p 'test_runner*.py' -v

12 new tests use genuine temporary bare-Git remotes, fetching, committing, leased pushing and readback. They cover competing push during intent, old token denial, scope restriction, preserved reporter file, stale HEAD, lost acknowledgement, unknown resolution and untrusted remote.

**Deliberately reproduced security RED:** test_old_agent_direct_push_is_possible_if_credentials_not_removed demonstrates that an Agent A with independent credentials can bypass this controller after fencing. A passing negative test does NOT mean production single-writer security is satisfied.

## Hard blockers for production RNR-06 completion

The library is NOT a deployed broker. The service principal, SSH host-key policy, operator/Owner authentication, database/signing-key isolation, removal of all runner-owned direct write credentials, recovery-worker quiescence attestations and scoped GitHub provider acceptance run remain unimplemented. The code does not create or change GitHub issues/PRs or DELP projections. It cannot protect any mutation path outside the trusted broker. HMAC keys and the external operator receipt do not authenticate the human Owner by themselves.

A temporary local Git remote is real Git CAS behavior, not a real GitHub acceptance certificate. Keep PR draft and Common #864 WP0 hold. Next: RNR-06B deployed isolated gateway and GitHub lab-only branch verification; RNR-07 cost/quality comparator.
