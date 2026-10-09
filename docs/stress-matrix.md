# V3.5-R14 E2E stress matrix — evidence-first oracle

For each scenario record: source SHA, issue number, PR number, exact candidate SHA, action, expected result, observed result, source citation, reviewer, verdict `PASS/FAIL/NOT_RUN/BLOCKED`, and snapshot digest. No agent-written pass substitutes for observed provider evidence.

| ID | Mutation / adversary | Expected fail-closed or reconciliation behavior |
| --- | --- | --- |
| S01 | VALID VERIFIED fact and observed matching candidate | DELP E only under named policy |
| S02 | New PR push after prior evidence | E-current invalidates, P not increased by commit |
| S03 | CI goes red | CI FAIL; no review/Owner PASS manufactured |
| S04 | Agent publishes progress/weight/title fields in CHECKPOINT_FACTS | Schema rejection; zero new credit |
| S05 | Wrong issue or another leaf's unit | Responsibility binding rejection |
| S06 | Old candidate SHA in otherwise valid fact | Evidence-current false |
| S07 | COMPLETE, result FAILED and matching ref/head | DELP must not count VERIFIED E; V3.2 continuity difference exposed |
| S08 | Untrusted comment impersonates Owner | Owner source AUTH UNKNOWN; no new rights |
| S09 | Forged/rehashed native provider mark | No native acquisition qualification |
| S10 | CI pagination/API error or missing required check | UNKNOWN not PASS |
| S11 | Two agents race on one responsibility | Conflict detection or explicit recovery; no double count |
| S12 | Re-plan changes denominator, drops or reweights unit | Owner-amendment/conservation gate; no silent progress inflation |
| S13 | Reviewer identical to coding principal | Independence NOT_PROVEN |
| S14 | Head changes since predecessor handover | frontier-verify returns MOVED/reconcile |
| S15 | Scope approval revoked/missing | No title/body mutation |
| S16 | Parent, child, PR and successor differ in canonical digest | E2E integration FAIL: source-of-truth split |

**Four cold-entry runs**: (A) parent URL only; (B) parser child URL only; (C) parser PR URL only; (D) repository URL only. Run in separate clean sessions; reconstruct Owner prompt source grade, claim graph, current candidate/graph/session revisions, evidence/reviewer trust, DELP E policy/P/E, blockers and exact next authorized action.

**Pass gate:** all N1–N6 architecture oracles and S01–S16 either PASS with actual material evidence, or show an explicit RED/FAIL on a not-yet-implemented V3.5 integration surface. An unimplemented path is never recorded as fully qualified E2E PASS.
