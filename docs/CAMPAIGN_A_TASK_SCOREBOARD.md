# Campaign A source-bound task scoreboard — not a DELP-derived programme score

**This checklist tracks experiment task execution only.** It is not V3.5 DELP P/E, not a progress percentage, not reviewer approval, and not an automatic publication. Status was observed in this author session on 2026-10-09. A different local agent must rerun/revalidate all required evidence itself.

| Task | Short name | Current execution result | Author checkpoint | Local-agent report expected |
| --- | --- | --- | --- | --- |
| T00 | Offline readiness | **PASS (scaffold only)**; app **EXPECTED_RED** | [Author T00 proof](https://github.com/reallaksh19/Common/issues/875#issuecomment-6076811230); `evidence/T00.md` and logs | Reproduce exact commands, post `TASK_EVIDENCE — T00` |
| T01 | Private GitHub repository + 3 issues | **BLOCKED LIVE**; repository 404 / `gh` not available. **SIMULATED T01 PREFLIGHT PASS 7/7** (not live GitHub) | [Author T01 blocker](https://github.com/reallaksh19/Common/issues/875#issuecomment-6076812912); `evidence/T01.md` | Create private repo; read back 3 actual issues; post T01 evidence |
| T01-PREFLIGHT | Seven hermetic bootstrap safety cases | **PASS 7/7 AUTHOR-SIDE SIMULATED_ONLY**, not live repo | [Simulator author evidence](https://github.com/reallaksh19/Common/issues/875#issuecomment-6076995572) | Post independent `TASK_EVIDENCE — T01-PREFLIGHT`; no provider PASS claim |
| T02 | Canonical DELP graph/decomposition/project | **NOT_RUN** | none | Post T02 evidence |
| T03 | Actual GitHub Actions expected RED | **NOT_RUN** | none | Post T03 evidence with job URLs |
| T04 | Parser draft PR and interrupted first agent | **NOT_RUN** | none | Post per-unit evidence and T04 record |
| T05 | Independent parser cold takeover | **NOT_RUN** | none | Post T05 evidence and source reconstruction |
| T06 | Independent review and governed parser merge | **NOT_RUN** | none | Reviewer verdict + authorized merge only |
| T07 | Reporter PR, CI and review | **NOT_RUN** | none | Post per-unit and T07 evidence |
| T08 | Live DELP/RELAY/V3.5 read-only comparison | **NOT_RUN** | none | Post genuine cross-engine RED/GREEN verdict |
| T09 | Publisher dry-run and sandbox-only authority | **NOT_RUN** | none | Post T09; live apply blocked absent approval |
| T10 | S01–S16 negative stress matrix | **NOT_RUN** | none | Post each case and T10 aggregate |
| T11 | Four isolated cold successors | **NOT_RUN** | none | Post four source entry transcripts + T11 |
| T12 | Final Campaign A reconciliation | **NOT_RUN** | none | Post TASK_RESULT with honest E2E readiness |

**Task-level pass rule:** current actual source/head, real command+exit and source artifacts, expected vs observed, reviewer grade, separate owner/writer grades; durable GitHub comment and readback. Current baseline is NOT a V3.5-R14 E2E acceptance certificate. Governing tracking: https://github.com/reallaksh19/Common/issues/875.

**Local agent work issue:** https://github.com/reallaksh19/Common/issues/877. This does not mean an RLL worker has been dispatched; authorization and runner smoke remain separate.

**T01-SIMULATED preflight:** `tests/test_harness_bootstrap.py` tests the actual shell bootstrap with hermetic fake `gh` and `git`. Seven simulator tests passed in two batches, including injection after R0 issue creation, refusing a public/existing repo, wrong auth, private happy path/actual ID binding, wrong target and duplicate rerun. This is not GH provider acceptance. See `evidence/T01-SIMULATED.md`. T01 live remains BLOCKED.
