#!/usr/bin/env python3
"""Locally tamper-evident, NOT identity-authenticating Campaign A task audit journal."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PIN = '13989969f6b7e432c4f7c1ddfe975449dba53593'
GENESIS = '0' * 64
TASKS = {f'T{i:02d}' for i in range(13)} | {'T01-PREFLIGHT'}
EVENTS = {
    'TASK_STARTED', 'TASK_EVIDENCE_DRAFTED', 'GITHUB_PUBLISHED',
    'GITHUB_READBACK_VERIFIED', 'BLOCKER_RECORDED',
    'REVISION_RECORDED', 'TASK_RESULT_RECORDED',
}
VERDICTS = {'PASS', 'FAIL', 'BLOCKED', 'NOT_RUN', 'EXPECTED_RED', 'UNKNOWN'}
_SHA = re.compile(r'^[0-9a-f]{40}$')
_URL = re.compile(r'^https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/(?:issues|pull)/[1-9][0-9]*(?:#issuecomment-[1-9][0-9]*)?$')


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')


def hash_bytes(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def digest_file(path: Path) -> str:
    if not path.is_file():
        raise ValueError(f'artifact not found: {path}')
    return hash_bytes(path.read_bytes())


def read_records(path: Path, *, check_artifacts: bool = True) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    prev = GENESIS
    for line_number, raw in enumerate(path.read_bytes().splitlines(), 1):
        try:
            entry = json.loads(raw)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise ValueError(f'line {line_number}: invalid JSON') from exc
        if not isinstance(entry, dict):
            raise ValueError(f'line {line_number}: event must be an object')
        digest = entry.get('event_hash')
        body = {k: v for k, v in entry.items() if k != 'event_hash'}
        if digest != hash_bytes(canonical(body)):
            raise ValueError(f'line {line_number}: event hash mismatch')
        if entry.get('sequence') != line_number or entry.get('previous_hash') != prev:
            raise ValueError(f'line {line_number}: sequence or predecessor hash mismatch')
        if entry.get('task') not in TASKS or entry.get('event') not in EVENTS or entry.get('verdict') not in VERDICTS:
            raise ValueError(f'line {line_number}: unknown task/event/verdict')
        if entry.get('protocol_pin') != PIN or entry.get('trust') != 'OPERATOR_ASSERTED_LOCAL_INTEGRITY_NOT_AUTHORITY':
            raise ValueError(f'line {line_number}: unsupported authority or protocol pin')
        if entry.get('event') in {'GITHUB_PUBLISHED', 'GITHUB_READBACK_VERIFIED'}:
            if not _URL.fullmatch(entry.get('github_url') or '') or '#issuecomment-' not in entry['github_url']:
                raise ValueError(f'line {line_number}: real GitHub issue-comment URL required')
        if check_artifacts:
            for item in entry.get('artifacts', []):
                path_s, claimed = item.get('path'), item.get('sha256')
                if not isinstance(path_s, str) or not isinstance(claimed, str):
                    raise ValueError(f'line {line_number}: malformed artifact item')
                # Do not accept path navigation into unrelated or secret areas.
                if Path(path_s).is_absolute() or '..' in Path(path_s).parts or not path_s.startswith('evidence/'):
                    raise ValueError(f'line {line_number}: artifact path must be local evidence/')
                observed = digest_file(Path(path_s))
                if claimed != observed:
                    raise ValueError(f'line {line_number}: artifact changed: {path_s}')
        prev = digest
        records.append(entry)
    return records


def append(args: argparse.Namespace) -> dict[str, Any]:
    if args.task not in TASKS or args.event not in EVENTS or args.verdict not in VERDICTS:
        raise ValueError('invalid task/event/verdict')
    if args.source_sha != 'UNKNOWN' and not _SHA.fullmatch(args.source_sha):
        raise ValueError('source SHA must be 40 lowercase hex or UNKNOWN')
    if not args.actor.strip() or len(args.actor) > 160 or not args.note.strip():
        raise ValueError('actor and bounded note required')
    if args.github_url and not _URL.fullmatch(args.github_url):
        raise ValueError('GitHub source URL must be an issue or PR permalink')
    if args.event in {'GITHUB_PUBLISHED', 'GITHUB_READBACK_VERIFIED'} and (
        not args.github_url or '#issuecomment-' not in args.github_url
    ):
        raise ValueError('provider publication/readback events require exact GitHub comment permalink')
    for path in args.artifact:
        if path.is_absolute() or '..' in path.parts or not path.as_posix().startswith('evidence/'):
            raise ValueError('artifact must be within evidence/ without traversal')
    args.ledger.parent.mkdir(parents=True, exist_ok=True)
    lock = args.ledger.with_suffix(args.ledger.suffix + '.lock')
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise ValueError(f'ledger lock exists; inspect before manual recovery: {lock}') from exc
    try:
        os.close(fd)
        entries = read_records(args.ledger)
        artifacts = [{'path': p.as_posix(), 'sha256': digest_file(p)} for p in args.artifact]
        now = datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')
        body = {
            'schema': 'V35_CAMPAIGN_A_AUDIT_EVENT_V1',
            'sequence': len(entries) + 1,
            'previous_hash': entries[-1]['event_hash'] if entries else GENESIS,
            'recorded_at_utc': now,
            'task': args.task,
            'event': args.event,
            'verdict': args.verdict,
            'actor': args.actor.strip(),
            'source_sha': args.source_sha,
            'protocol_pin': PIN,
            'repository': 'reallaksh19/relay-v35-e2e-lab',
            'github_url': args.github_url or None,
            'note': args.note.strip(),
            'artifacts': artifacts,
            'trust': 'OPERATOR_ASSERTED_LOCAL_INTEGRITY_NOT_AUTHORITY',
        }
        body['event_hash'] = hash_bytes(canonical(body))
        # Exclusive lock is held. Reopen and append; never modify previous lines.
        with args.ledger.open('ab') as journal:
            journal.write(canonical(body) + b'\n')
            journal.flush()
            os.fsync(journal.fileno())
        return body
    finally:
        lock.unlink(missing_ok=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Append and validate local audit hashes (NOT authorization)')
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('append')
    p.add_argument('--ledger', type=Path, required=True)
    p.add_argument('--task', required=True, choices=sorted(TASKS))
    p.add_argument('--event', required=True, choices=sorted(EVENTS))
    p.add_argument('--verdict', required=True, choices=sorted(VERDICTS))
    p.add_argument('--actor', required=True)
    p.add_argument('--source-sha', default='UNKNOWN')
    p.add_argument('--github-url')
    p.add_argument('--artifact', type=Path, action='append', default=[])
    p.add_argument('--note', required=True)
    v = sub.add_parser('verify')
    v.add_argument('--ledger', type=Path, required=True)
    try:
        args = parser.parse_args(argv)
        if args.command == 'append':
            event = append(args)
            print(f"AUDIT_APPENDED seq={event['sequence']} task={event['task']} hash={event['event_hash']} (LOCAL INTEGRITY ONLY)")
        else:
            if not args.ledger.exists():
                print(f'AUDIT_NOT_STARTED path={args.ledger} records=0 (no PASS claim)')
                return 0
            entries = read_records(args.ledger)
            print(f"AUDIT_CHAIN_VALID records={len(entries)} tail={entries[-1]['event_hash'] if entries else GENESIS} (NOT PRINCIPAL AUTHORITY)")
        return 0
    except (ValueError, OSError, TypeError) as exc:
        print(f'AUDIT_REJECTED: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
