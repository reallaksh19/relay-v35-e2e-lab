# Campaign A audit index — human navigation, not evidence authority

**Common source pin:** `13989969f6b7e432c4f7c1ddfe975449dba53593`.  
**Canonical GitHub tracking:** [programme #864](https://github.com/reallaksh19/Common/issues/864), [lab campaign #875](https://github.com/reallaksh19/Common/issues/875), [bounded manual-agent task #877](https://github.com/reallaksh19/Common/issues/877).  
**Archive version:** V3 task protocol, produced in assistant session; SHA256 and file manifest must be checked against the actual delivered archive.  
**Live lab repository:** **NOT CREATED at pre-packaging observation**; verify at execution time.  
**Independent local-agent reports:** NONE as of pre-packaging observation. Do not treat author evidence as independent reviewer approval.

| Checkpoint | GitHub durable record | Authority and result |
| --- | --- | --- |
| R12 prerequisite | [PR #861](https://github.com/reallaksh19/Common/pull/861) | Merged; independent review debt [#869](https://github.com/reallaksh19/Common/issues/869) open |
| V3.5 WP0 architecture | [#866 source audit](https://github.com/reallaksh19/Common/issues/866#issuecomment-6075962195) | Proposed, not two independent source reviews |
| Campaign A preflight T00 | [T00 author evidence](https://github.com/reallaksh19/Common/issues/875#issuecomment-6076811230) | Offline harness 12/12 PASS, feature suite EXPECTED_RED, not local-agent independent |
| T01 live creation | [T01 blocker](https://github.com/reallaksh19/Common/issues/875#issuecomment-6076812912) | Real repo BLOCKED, 404; no lab issue numbers |
| T01 mock bootstrap | [Simulator author evidence](https://github.com/reallaksh19/Common/issues/875#issuecomment-6076995572) | Seven mock cases passed; not real GitHub |
| Local-agent handoff | [#877 bounded instructions](https://github.com/reallaksh19/Common/issues/877#issuecomment-6077005737) | Manual prompt prepared, not a worker dispatch |
| T02–T12 | NONE | NOT_RUN on real lab as of pre-packaging observation |

When agent executes:

1. Check the live repo/issue/PR before repeating any operation.
2. Run/record task; create `TASK_EVIDENCE — Tnn` issue comment; independently fetch and compare exact published text.
3. Append task, publication and readback audit events; verify `events.jsonl` hash chain and source artifact hashes.
4. Add a **new** row with GitHub permalink, exact source SHA, task verdict and observed next; don't overwrite or relabel previous task evidence. If a correction is needed, append a corrective row and link the original.
5. Publish T12 `TASK_RESULT` only with traceable references to every prior task, explicit blockers and distinct independent identities.
