# V3.5 Campaign A audit trail contract

The evidence chain is **three-layered**, not one opaque evidence claim:

1. **Source layer:** exact git commit for Common and lab, canonical GitHub issue/PR/CI/comment URL, material SHA, read time, and role-specific plan/source/candidate revision.
2. **Observation layer:** actual sanitized command log, exit status, CI job and reviewer identity grades, file hashes, and expected/observed comparisons. Local output is operator-asserted, not a GitHub provider signature.
3. **Durability layer:** one `TASK_EVIDENCE — Tnn` comment per completed or blocked task on Common #875, *separate* GitHub GET/readback, and a local digest-chained ledger entry referring to the canonical comment URL. Corrections are NEW entries/comments linked to superseded records, never retrospective silent edits.

## Local integrity ledger

- Location: `evidence/audit/events.jsonl` (created by first `append`, not shipped with claimed task results).
- CLI: `python3 scripts/audit_trail.py append --ledger evidence/audit/events.jsonl --task T00 --event TASK_EVIDENCE_DRAFTED --verdict PASS --actor agent-session-label --source-sha UNKNOWN --artifact evidence/logs/T00-readiness.log --note 'offline readiness only'`.
- Verify: `python3 scripts/audit_trail.py verify --ledger evidence/audit/events.jsonl`.
- Each line has `sequence`, `previous_hash`, `event_hash` (SHA-256 canonical JSON content), UTC timestamp, task, event kind, grade, asserted actor, material SHA, optional GitHub URL, a digest for **every** attached local artifact, and an explicit `integrity_not_authority` marker.
- Events: `TASK_STARTED`, `TASK_EVIDENCE_DRAFTED`, `GITHUB_PUBLISHED`, `GITHUB_READBACK_VERIFIED`, `BLOCKER_RECORDED`, `REVISION_RECORDED`, `TASK_RESULT_RECORDED`.
- Appending uses an exclusive `.lock` file to fail closed on concurrent writers; if the agent crashes while holding a stale lock, manually inspect and reconcile the ledger before removing it. **Do not bypass checksum verification** after interruption.
- `verify` checks sequence, record hashes, previous hash links, allowed task IDs/verdicts and attached file digests if files exist. If a referenced artifact is missing, verification FAILS. Any changed ledger bytes or artifact content fail verification. Note that a malicious author could regenerate an entire chain: this is **tamper-evident local consistency**, not tamper-proof, person-identity-proof or time-notarized evidence.

## GitHub evidence publication procedure

1. Generate a **draft**, review it and redact secrets. Verify SHA/graph/facts identity with actual GitHub sources. Never write P/E into CHECKPOINT_FACTS; do not claim reviewer identity without an independent principal and source witness.
2. Publish *one* issue comment with `gh issue comment 875 --repo reallaksh19/Common --body-file evidence/Tnn-local.md` (read-only task publisher is not a production application scoreboard writer).
3. Record provider-created comment ID/URL from the CLI/API; GET the exact comment using `python3 scripts/verify_github_comment.py --comment-id <ID> --body-file evidence/Tnn-local.md --expected-author <LOGIN>`; this performs a GitHub API read, exact URL/issue/author/body comparison and prints the body SHA only on success. Compare body with published file **bytewise or a canonical digest**; URL alone is not readback. Record observed HEAD/PR/CI in the evidence.
4. Append **distinct** `GITHUB_PUBLISHED` and `GITHUB_READBACK_VERIFIED` events, with actual comment URL, observed body SHA and cross-referenced draft. Do not assert these events if no API readback happened.
5. Link the same comment in local `docs/CAMPAIGN_A_TASK_SCOREBOARD.md`, but treat that file as a disposable human cache, not source authority.
6. If GitHub down/auth missing: post nothing falsely, save draft locally, append a BLOCKER event, mark task BLOCKED, and stop subsequent stages that require durability.

## External audit checkpoint per task

Use all of these fields, making UNKNOWN explicit: task ID; protocol HEAD and lab material HEAD; repository and issue/PR; authenticated operator vs asserted session; source roles and policy versions; expected and observed oracles; exact commands and exits; log hashes; CI run/job URLs; reviewer principal and verdict; source privacy grade; GitHub comment URL/readback witness; open negative knowledge; blocker; next task; corrective/supersedes refs. Any missing mandatory source means `NOT_RUN` or `BLOCKED`, not inferred success.

## Threat model / invariants

- Replay of a valid-looking checksum does not grant GitHub principal, Owner, review, merge, release or publication authority.
- A CURRENT material HEAD does not prove a candidate passed a required test policy, has independent review, or represents production acceptance.
- A failed/stale fact must not receive E under a policy that requires VERIFIED/current evidence.
- An interrupted local agent never spawns a new responsibility or silently discards prior evidence.
- A changed plan, candidate, reviewer decision or evidence must invalidate all downstream derived views until reconciliation.
- Never expose tokens, user files, source comments containing private data, `gh auth` output with secrets, or raw personal chat content into public Common comments.
