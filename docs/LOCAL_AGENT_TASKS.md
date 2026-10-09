# V3.5-R14 Campaign A — LOCAL AGENT RUNBOOK v3

**PRIMARY LOCAL AGENT PROMPT:** [`../AGENT_START_HERE.md`](../AGENT_START_HERE.md); see also `EXPECTED_OUTCOMES.md`, `AUDIT_TRAIL_SPEC.md`, `TASK_EVIDENCE_TEMPLATE.md`. Each task requires a new GitHub evidence comment + provider readback and local hash-chain event.

**Governing authority:** `reallaksh19/Common` #787 → #864 → #875.
**Implementation under test:** existing Common V3.2 + V3.5 components, pinned to `13989969f6b7e432c4f7c1ddfe975449dba53593`. The full V3.5-R14 end-to-end integration **does not yet exist**.
**Lab-only target:** `reallaksh19/relay-v35-e2e-lab` (PRIVATE). **Synthetic Owner source, never authenticated real chat.**
**Scope:** Test, publish accurately observed task evidence, and report defects. Do not repair frozen Common V3.2 or start #864 WP1, grant approval, merge, or enable general-purpose GitHub writers.

## When the local agent can start

- **Right now:** T00 *offline* in a clean extraction of the ZIP, no GitHub rights required. First check local source and self-tests, record expected RED app, validate package and shell syntax. Publish a `TASK_EVIDENCE` comment to Common #875 when authorized GitHub `gh` access exists, otherwise preserve the local evidence file.
- **After private GitHub provisioning:** T01–T03 as soon as the agent has `git`, `gh` (authenticated permission to create a private repo and issues), Python 3.11+, PyYAML and an exact-sha `Common` checkout. A separate isolated agent/reviewer is required for later T05/T06 and T11 independence claims.
- **Only when the prior task's evidence and readback are recorded:** advance to the next task. `BLOCKED`/`NOT_RUN` do not satisfy a gate. `EXPECTED_RED` is not an E2E pass.

## Per-task execution and authoritative evidence (checklist)

**T00 — Local readiness (NOW; expected PASS + RED application)**
- [ ] Extract the archive, inspect synthetic Owner intent; record ZIP SHA256 and Common source pin.
- [ ] Run `bash -n scripts/*.sh` separately; run `python3 -m compileall -q scripts src tests`.
- [ ] Run `PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_harness*.py' -v` → harness passes.
- [ ] Run `PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_inventory*.py' -v` → **expected failing** initial application tests, record exact exit code and failing names.
- [ ] Capture command transcript, actual environment versions, files and SHA, output `evidence/T00.md`; label `PASS_WITH_EXPECTED_RED` only in prose, reporter verdict `PASS` for readiness (NOT E2E).

**T01-PREFLIGHT — Hermetic bootstrap safety test (NOW; optional extra independent source check)**
- [ ] In a clean extraction, run `PYTHONPATH=tests python3 -m unittest -v test_harness_bootstrap.BootstrapMockBoundary.test_existing_private_or_public_repo_never_reused_without_reconcile test_harness_bootstrap.BootstrapMockBoundary.test_interrupted_child_issue_creation_blocks_retry test_harness_bootstrap.BootstrapMockBoundary.test_missing_gh_auth_denies_without_side_effect`.
- [ ] Run the remaining four tests separately as documented in `evidence/T01-SIMULATED.md`; the scripts mock `gh` and `git` only inside temporary directories; **they DO NOT create a GitHub repo**.
- [ ] Verify seven simulator tests pass, including interrupted R0/R1/R2 creation, no duplicate rerun, exact repository allowlist, and private-only creation. Record each command and exit/log checksum as `TASK_EVIDENCE — T01-PREFLIGHT` on Common #875. Do NOT label real T01 as PASS.

**T01 — Private repo creation and identity binding (AFTER GH ADMIN/REPO RIGHTS)**
- [ ] `gh auth status`; `gh repo view reallaksh19/relay-v35-e2e-lab` should initially report not found.
- [ ] From the pristine extracted scaffold, `bash scripts/bootstrap_lab.sh reallaksh19/relay-v35-e2e-lab` (script is **one-shot**, fails closed on partial state).
- [ ] Read back GitHub visibility=PRIVATE, main SHA, 3 real R0/R1/R2 issue URLs, `.relay/issue-map.json`, `graph.yaml` refs; confirm role ownership and dependency.
- [ ] Publish `TASK_EVIDENCE` T01 with provider URLs + exact SHA + command log to Common #875; no automatic PR or merge.

**T02 — Canonical DELP graph and initial projection**
- [ ] Check out Common exact SHA `13989969f6b7e432c4f7c1ddfe975449dba53593` alongside the lab.
- [ ] `bash scripts/run_baseline.sh ../Common` → `validate-graph`, `decompose-check ENFORCED`, `project`; capture full output and exit statuses.
- [ ] Inspect generated `.relay/projection.json`: both leaves, dependencies, policy and progress; no claim of real evidence/reviewer/Owner grade from fixture.
- [ ] Compare `programme.repository` and issue/child refs to GitHub readback; T02 `PASS` needs actual canonical DELP execution, not harness-only success.

**T03 — Expected RED GitHub CI baseline**
- [ ] Read real default-branch SHA; run/inspect `.github/workflows/inventory.yml` at that SHA, Python 3.11+3.12 matrix.
- [ ] Harness jobs should pass and app tests should **fail on expected NotImplementedError**. Classify `EXPECTED_RED` only with exact Actions run/job IDs and logs; unexpected workflow/security/test failures are `FAIL`, not expected RED.
- [ ] Publish T03 evidence with real GitHub Actions URLs and zero fabricated pass/skip counts.

**T04 — Parser PR A, limited first-agent work**
- [ ] Create `lab/parser` from actual main SHA and draft PR linked to R1; update plan's `primary_pr` via explicit plan revision (never infer progress from PR creation).
- [ ] Agent A implements parser U01 then U02, with exact-head tests; preserve `TASK_EVIDENCE` per **unit** with refs, current candidate SHA, command logs and no hand-authored P/E.
- [ ] **Stop agent after U02** with remaining U03 incomplete; record predecessor's last observed SHA and session identity.

**T05 — Independent cold takeover on *same* R1 issue**
- [ ] Launch a truly separate agent execution without predecessor chat, provide only R1 issue or immutable repo pointer.
- [ ] Reconstruct Owner mirror/source grade, graph, PR SHA, accepted facts, next U03; compare to verifier oracle.
- [ ] Complete U03, run exact-head local/Actions tests. Record SHA move → stale E and refreshed evidence before any merge.

**T06 — Independent parser review, separately authorized merge**
- [ ] Different reviewer principal/source run verifies parser code, negative fixtures, actual CI and evidence.
- [ ] Record explicit review verdict; self-review is `INDEPENDENCE_NOT_PROVEN`.
- [ ] **Do not merge** without explicit scoped Owner/Coordinator merge instruction. A technically mergeable PR with no independent qualified review is not PASS.

**T07 — Reporter PR B, implementation, review**
- [ ] Preserve parser dependency: create reporter branch only when parser requirements are materially satisfied; if merge blocked, mark `BLOCKED` or use an explicit tested immutable dependency, not a fake pass.
- [ ] Implement deterministic Decimal totals, sorted output and CLI; each U01/U02/U03 has a separate completion/evidence checkpoint.
- [ ] Exact-head CI and separate reviewer verdict. No automatic merge.

**T08 — V3.2 native DELP + V3.5 read-only replay**
- [ ] Read provider facts from real GitHub; run canonical `project`, `admit`, `frontier`, `frontier-verify` and `sync-github --dry-run` under pinned source.
- [ ] Run V3.5 `integration_cold_entry_v35.py` and `integration_relay_consumers_v35.py` for parent/child/PR source URLs; pending approvals must return explicit `HOLD`, not green.
- [ ] Record source identity roles: GRAPH_REVISION vs SESSION_SOURCE_COMMIT vs CODE_CANDIDATE_HEAD and compare output digests/next. Missing R3B→programme DELP join is **expected integration RED**, not a functional E2E pass.

**T09 — Sandbox-only publication guard**
- [ ] Confirm dry-run makes **zero** writes; check actual GitHub issue/PR readback.
- [ ] Without separately verified sandbox-scoped graph approval, scoreboard approval and Owner authorization, `--apply` stays **BLOCKED/OFF**.
- [ ] If separately authorized, exercise guarded publication, readback, manual-text preservation, revoked approval and drift rejection only in private lab.

**T10 — Sixteen adversarial source/evidence scenarios**
- [ ] Execute S01–S16 in `docs/stress-matrix.md`, each with expected vs observed source, exact material, exit codes and PASS/FAIL/NOT_RUN/BLOCKED.
- [ ] Verify PR HEAD push invalidates stale E; failed result does not become E; fabricated P/E fields reject; forged native and impersonated Owner have no authority.
- [ ] Do not count tests that are mocked/UNCONNECTED as native provider successes.

**T11 — Four isolated cold-successor entries**
- [ ] Four distinct clean executions from parent-only, child-only, PR-only and repository-only pointers, never predecessor chat.
- [ ] Reconstruct original *synthetic* Owner intent grade, plan DAG, unit & candidate, DELP P/E under named policy, independent review, next authorized step and Unknowns.
- [ ] Compare results to separate GitHub material oracle; record unsupported claims and disagreement as failures.

**T12 — Final truth reconciliation and release disposition**
- [ ] Attach exact tested SHAs, full PASS/FAIL/BLOCKED matrix, source-to-consumer call-edge trace, provider-backed CI/reviewer evidence and four cold reports.
- [ ] Publish result: `CAMPAIGN_A_REALITY_TESTED` (if proven) versus `V35_R14_E2E_NOT_QUALIFIED` until missing WP0/#866 and WP1–WP8 join are actually completed.
- [ ] Do not imply #787 AC1–AC8 or production live writer acceptance from a disposable lab.

## Mandatory per-task evidence record after **each** task

1. Capture an immutable log or command transcript in `evidence/logs/`, showing the **actual command, exit code and source head**. Redact any secrets. Run `scripts/task_evidence.py` to create `evidence/Tnn.md`; this generator records provenance but **does not certify it**.
2. Review the generated draft. It must include: task ID, operator/session, pinned Common SHA, GitHub lab repo/issue/PR refs when observed, exact commit SHA, graph/facts revision, expected vs observed, command/log SHA256, local/Actions test counts and skips (or UNKNOWN), next step and any blocker. No agent-authored P/E.
3. Where GitHub credentials allow, publish the draft to [Common #875](https://github.com/reallaksh19/Common/issues/875) **as a new `TASK_EVIDENCE — Tnn` comment**, using `gh issue comment 875 --repo reallaksh19/Common --body-file evidence/Tnn.md`. Check the created comment in GitHub and capture its permalink; a local file alone is not a durable GitHub publication.
4. If responsibility R1/R2 started and the canonical DELP data is valid, also publish the correct `CHECKPOINT_FACTS_V1` in its **lab child issue** only when actual candidate SHA, verification result and durable evidence refs have been independently verified. Do not manufacture a facts block from task-level readiness.
5. **Do not proceed** when required task evidence is absent, `BLOCKED`, or `NOT_RUN`. `EXPECTED_RED` qualifies only the explicitly expected negative baseline; it never establishes feature completion or V3.5 integration acceptance.

## Example local agent invocation for T00

```bash
mkdir -p evidence/logs
( echo 'COMMAND: python3 -m unittest discover -s tests -p test_harness*.py -v'; \
  PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_harness*.py' -v; \
  echo "EXIT_CODE=$?" ) > evidence/logs/T00-harness.log 2>&1
python3 scripts/task_evidence.py --task T00 --verdict PASS --operator 'local-agent-session-1' \
  --expected 'Harness PASS; app feature tests expected RED' \
  --observed 'Harness checks pass; inventory feature tests intentionally unimplemented' \
  --log evidence/logs/T00-harness.log --artifact docs/local-baseline-result.json \
  --next 'Provision PRIVATE GitHub lab; T01' \
  --output evidence/T00.md
```

This example is a **format example only**; it does not replace full T00 log capture or independently verify tests.

## V3 chained evidence requirement

The local agent must run `python3 scripts/audit_trail.py append ...` for each bounded TASK_EVIDENCE draft, then record genuine GitHub publication and separate provider readback only after those happened. Verify `python3 scripts/audit_trail.py verify --ledger evidence/audit/events.jsonl` before each new append and on T12. The local ledger is integrity evidence only, not a GitHub attestation. Review and redact every log before publication. Full reference: `docs/AUDIT_TRAIL_SPEC.md`.
