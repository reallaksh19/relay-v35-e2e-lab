# TASK_EVIDENCE — T01-SIMULATED — PASS (hermetic mocks only)

- **Task:** T01 preflight for real bootstrap, NOT T01 live private repository creation
- **Repository source:** `Common@13989969f6b7e432c4f7c1ddfe975449dba53593`; no local Common checkout or native DELP execution
- **Test target:** `scripts/bootstrap_lab.sh` + `tests/test_harness_bootstrap.py` in Campaign A scaffold
- **Operator:** current ChatGPT author session, not independent local agent
- **Owner source:** `SYNTHETIC_LAB_ONLY`; original source grade UNKNOWN outside lab
- **Material HEAD / PR / GitHub CI:** NOT_OBSERVED / NOT_CREATED / NOT_RUN
- **Local environment:** Python 3.13.5; stdlib unittest; PyYAML installed; shell bash

## Checklist and independently rerunnable commands

- [x] `bash -n scripts/bootstrap_lab.sh`; Python `compileall -q scripts src tests` → exit 0
- [x] Simulator batch 1, **3/3 tests PASS**, EXIT_CODE=0; exact command + log SHA in `evidence/logs/T01-simulator-1.log`
- [x] Simulator batch 2, **4/4 tests PASS**, EXIT_CODE=0; exact command + log SHA in `evidence/logs/T01-simulator-2.log`
- [x] Previous harness batch **12/12 PASS**, EXIT_CODE=0, `evidence/logs/T01-existing-harness.log`
- [x] Toy application **6 tests / 7 expected NotImplementedError errors**, EXIT_CODE=1, `evidence/logs/T01-app-expected-red.log`
- [x] Bootstrap restricts its target to exactly `reallaksh19/relay-v35-e2e-lab` and still checks private-only repository existence; accidental rerun/refusal proven only in simulated CLI
- [ ] **REAL T01:** private repository creation, actual GitHub issues, graph upload, source SHA/readback and hosted CI → BLOCKED; repo 404 and no GitHub administrative create action in this session

### Simulated scenario oracle

| Scenario | Observed | Qualification |
|---|---|---|
| Missing GH authentication | No remote simulated side effects | MOCK PASS |
| Public repo exists | Refused before adding lab issues | MOCK PASS |
| Private repo exists | Refused before adding duplicate lab issues | MOCK PASS |
| First private bootstrap | Simulated issues #11/#12/#13, graph bound to them | MOCK PASS |
| Interrupt after parent issue | Returns injected failure and blocks unsafe rerun | MOCK PASS |
| Repeat completed bootstrap | Refuses; issue count stays three | MOCK PASS |
| Target another repo including Common | Refuses before GH actions | MOCK PASS |

### Exact command invocations and log integrity

- **Batch 1:** `PYTHONPATH=tests python -m unittest -v test_harness_bootstrap.BootstrapMockBoundary.test_existing_private_or_public_repo_never_reused_without_reconcile test_harness_bootstrap.BootstrapMockBoundary.test_interrupted_child_issue_creation_blocks_retry test_harness_bootstrap.BootstrapMockBoundary.test_missing_gh_auth_denies_without_side_effect`
- **Batch 2:** `PYTHONPATH=tests python -m unittest -v test_harness_bootstrap.BootstrapMockBoundary.test_one_shot_private_happy_path_assigns_actual_issue_numbers test_harness_bootstrap.BootstrapMockBoundary.test_refuse_alternative_repository_before_any_repo_action test_harness_bootstrap.BootstrapMockBoundary.test_refuse_prod_repository_before_any_repo_action test_harness_bootstrap.BootstrapMockBoundary.test_rerun_cannot_duplicate_issues_after_success`
- `evidence/logs/T01-simulator-1.log`: `sha256:139fd151ad9f1a8ce7a1ddcbe90daf871d1a8cde6e961fe5e1b7f899ea5cc50b`
- `evidence/logs/T01-simulator-2.log`: `sha256:bbd6e2798e2369c5d7384297633edd0ba176fd48eeb3d3b5231c772cdd3eb7b7`
- `evidence/logs/T01-existing-harness.log`: `sha256:bd22a80612996e312b915c50eec13e99cc480744ffcf8cad077fb1ec89ee48d2`
- `evidence/logs/T01-app-expected-red.log`: `sha256:dbb2c65d329103520a50941a00044a856cdb36434b5a872a178da27a40be8e0a`

**Verdict:** `T01_SIMULATED_BOOTSTRAP_PREFLIGHT=PASS` (7/7); `T01_REAL_PROVIDER=BLOCKED`. This does not grant DELP progress, independent review, Owner original authentication, production GitHub writer, or any V3.5 programme acceptance. **Next:** independently run actual private `gh` bootstrap and publish task evidence with GitHub issue IDs/HEAD, after authorized repository creation.
