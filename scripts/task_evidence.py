#!/usr/bin/env python3
"""Generate a provenance-labeled draft of per-task TASK_EVIDENCE (no GH writes).

A SHA256 digest shows file integrity, not command authenticity, independent review,
original Owner authorship or eligible DELP credit. Only actual human-reviewed GitHub
observations are evidence. This script never invents P/E, reviewer verdict or CI PASS.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import re
import sys

PIN = '13989969f6b7e432c4f7c1ddfe975449dba53593'
IDS = tuple(f'T{i:02d}' for i in range(13)) + ('T01-PREFLIGHT',)
VERDICTS = ('PASS', 'FAIL', 'BLOCKED', 'NOT_RUN', 'EXPECTED_RED')
SHA = re.compile(r'[0-9a-f]{40}\Z')

def digest_file(path: Path) -> str:
    if not path.is_file():
        raise ValueError(f'missing evidence artifact: {path}')
    return sha256(path.read_bytes()).hexdigest()

def make_record(a: argparse.Namespace) -> str:
    if a.verdict in ('PASS', 'FAIL', 'EXPECTED_RED') and not a.log:
        raise ValueError(f'{a.verdict}: a real command/observation log is required')
    if a.verdict == 'PASS' and (not a.expected.strip() or not a.observed.strip()):
        raise ValueError('PASS requires expected and observed detail')
    if a.sha and not SHA.fullmatch(a.sha):
        raise ValueError('SHA must be full lowercase 40-hex commit')
    if not a.operator.strip() or not a.expected.strip() or not a.observed.strip() or not a.next.strip():
        raise ValueError('operator, expected, observed and next are required')
    artifacts = list(dict.fromkeys(a.log + a.artifact))
    proof = [f'- `{p}`: sha256:{digest_file(Path(p))}' for p in artifacts]
    log_text = '\n'.join(Path(p).read_text(encoding='utf-8', errors='replace') for p in a.log)
    exit_codes = [int(x) for x in re.findall(r'(?m)^EXIT_CODE=([0-9]+)\s*$', log_text)]
    if not exit_codes and a.verdict in ('PASS', 'FAIL', 'EXPECTED_RED'):
        raise ValueError('log missing standalone EXIT_CODE=; record actual command exit status')
    if a.verdict == 'PASS' and any(x != 0 for x in exit_codes):
        raise ValueError('PASS denied: attached command log contains nonzero EXIT_CODE')
    if a.verdict in ('FAIL', 'EXPECTED_RED') and not any(x != 0 for x in exit_codes):
        raise ValueError(f'{a.verdict} denied: attached command log contains no nonzero EXIT_CODE')
    source = f'{a.sha}' if a.sha else 'NOT_OBSERVED'
    stamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    rows = [
        f'## TASK_EVIDENCE — {a.task} — {a.verdict}',
        '',
        f'- **Observed at (UTC):** {stamp}',
        f'- **Operator/session (asserted, not identity-authenticated):** `{a.operator}`',
        f'- **Protocol source (pinned):** `reallaksh19/Common@{PIN}`',
        '- **Test repository:** `reallaksh19/relay-v35-e2e-lab` (sandbox only)',
        f'- **Actual material SHA:** `{source}`',
        f'- **Issue:** `{a.issue or "UNKNOWN/NOT_CREATED"}`',
        f'- **PR:** `{a.pr or "UNKNOWN/NOT_CREATED"}`',
        '- **Owner original source:** `SYNTHETIC_LAB_ONLY`',
        '- **V3.5 programme acceptance:** `AC0/8` (not derived from this check)',
        '- **Production writer / automatic merge:** `OFF`',
        '', '### Checklist (operator must verify each item, not auto-checked)',
        '- [ ] Exact source/branch/issue scope read from GitHub or local Git',
        '- [ ] Real commands and exit codes retained, secrets redacted',
        '- [ ] Expected behavior compared against actual output',
        '- [ ] GitHub CI/reviewer/Owner authority graded separately (or UNKNOWN)',
        '- [ ] Evidence published to Common #875 and read back before advancing',
        '', '### Expected', '', a.expected, '', '### Observed (agent assertion; verify via attached source)', '', a.observed,
        '', '### File digests (integrity, not authentication)', '', *(proof or ['- NONE']),
        '', '### Qualification', '',
        f'`{a.verdict}` only for task {a.task}; no broader V3.5 acceptance, DELP E or merge authority.',
        '', '### Blocker / next action', '', a.next,
        '', '### GitHub durability', '', 'NOT_PUBLISHED_BY_THIS_LOCAL_GENERATOR; publish to Common #875 and read back.', ''
    ]
    return '\n'.join(rows)

def main(argv=None) -> int:
    p = argparse.ArgumentParser(description='Generate honest task-evidence draft with local file hashes')
    p.add_argument('--task', required=True, choices=IDS)
    p.add_argument('--verdict', required=True, choices=VERDICTS)
    p.add_argument('--operator', required=True)
    p.add_argument('--expected', required=True)
    p.add_argument('--observed', required=True)
    p.add_argument('--next', required=True)
    p.add_argument('--sha')
    p.add_argument('--issue')
    p.add_argument('--pr')
    p.add_argument('--log', action='append', default=[])
    p.add_argument('--artifact', action='append', default=[])
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args(argv)
    try:
        record = make_record(a)
    except (ValueError, OSError) as e:
        print(f'TASK_EVIDENCE_DENIED: {e}', file=sys.stderr)
        return 2
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(record, encoding='utf-8')
    print(f'DRAFT_WRITTEN {a.output} (NOT GITHUB PUBLISHED; NOT INDEPENDENTLY QUALIFIED)')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
