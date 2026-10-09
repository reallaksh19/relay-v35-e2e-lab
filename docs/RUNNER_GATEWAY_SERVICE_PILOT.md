# RNR-06B — Private broker service and deployment boundary (LAB ONLY)

**Status:** local implementation + test evidence; no real GitHub credential-isolated deployment, no independent acceptance, no production writer. Tracks lab issue #9 / draft PR #10. Common #864 WP1 HOLD and #787 AC0/8 remain unchanged.

## Implemented

- scripts/runner_gateway.py: Linux AF_UNIX socket, SO_PEERCRED agent-UID verification, strict one-frame WRITE schema, bounded base64 payload, no user-selected remote, branch, grant, promotion, recovery, bootstrap, issue or PR endpoints. Response is a sanitized COMMITTED, DENIED or HOLD.
- scripts/runner_gateway_service.py: separate runnable broker service process. LAB local bare-Git test mode; GitHub-lab mode restricted to exact reallaksh19/relay-v35-e2e-lab remote and disposable lab/runner-provider-sandbox branch.
- scripts/runner_provider.py: Git subprocess strips ambient HOME, SSH_AUTH_SOCK, Git config and arbitrary SSH command. GitHub transport requires operator-owned non-symlink private SSH identity and known-hosts file, strict host checking, no inherited ssh-agent. Provider loss preserves UNKNOWN custody state.
- Tests: 101 native test cases across RNR-01–06B, including real local bare-Git commits/CAS, subprocess client+server, fenced epoch, malformed payloads, duplicate keys, privilege escalation, SSH mode, interrupted provider HOLD and unsafe startup denial.

## Run local tests

    python -m py_compile scripts/runner_pilot.py scripts/runner_stage2.py scripts/runner_custody.py scripts/runner_provider.py scripts/runner_gateway.py scripts/runner_gateway_service.py
    python -m unittest discover -s tests -p 'test_runner*.py' -v

The 101 test figure applies to the local pilot, NOT a GitHub-hosted run.

## Lab-only service launch

Before launching, a trusted operator creates a private folder (0700), private signing key (0600), bootstraps the LAB-R1 custody DB and chooses a disposable bare Git remote. The process command:

    python scripts/runner_gateway_service.py --mode lab-local \
      --socket /private/operator/runner.sock \
      --db /private/operator/custody.sqlite \
      --operator-key-file /private/operator/signing.key \
      --client-uid CLIENT_UNIX_UID \
      --local-remote /tmp/disposable-bare.git

An explicit unsafe flag --allow-same-uid-in-lab-tests is available ONLY for local tests, never for github-lab mode. No operator privileges are exposed over the socket.

## Unproven deployment requirements — DO NOT CLAIM COMPLETION

1. **Real principal separation:** broker and agent must run under different Unix identities; the correct UID must be observed via SO_PEERCRED. Local tests use same UID with unsafe opt-in and do not establish real separation.
2. **Socket ACL:** the broker parent directory is 0700 and the socket 0600 by default. A cross-UID agent therefore cannot access it until an operator separately provisions an exact POSIX ACL for traverse/connect WITHOUT exposing key/DB files. Until then deployment is correctly fail-closed.
3. **Credential custody:** provision a private GitHub SSH key only to the broker. Confirm every old-agent GitHub token, app, workflow, SSH key and other direct-write path has been revoked or denied. A GitHub deploy key alone does not guarantee branch-specific permissions; enforce branch-level restrictions separately.
4. **Operator approval:** HMAC and an arbitrary operator receipt do not authenticate an Owner. Establish real human authorization, a privileged control service and provenance for each promotion.
5. **UNKNOWN recovery:** opaque quiescence strings are not proof that an old Git push cannot complete late; use authenticated worker shutdown, provider readback and independent evidence before releasing HOLD.
6. **Real GitHub acceptance:** demonstrate a broker-initiated write/readback on ONLY the disposable lab branch, a racing writer rejected, and direct old-agent mutation denied. Local Git CAS tests are not real GitHub acceptance.
7. **Hosted exact-head verification:** GitHub Actions Python 3.11/3.12 and independent source review must qualify the PR. Prior hosted jobs failed without assigned runners or test steps; do not treat a workflow failure as a passing test.
8. **Lifecycle and ROI:** neither programme DELP scoreboard nor Owner responsibility/decomposition was changed by this prototype. RNR-07 benchmark comparison remains open.

**Verdict:** locally implemented executable broker service and negative oracles; NOT deployed, credential-isolated, provider-qualified or merge-ready. Preserve Common WP0 hold, production writer OFF and draft PR status.
