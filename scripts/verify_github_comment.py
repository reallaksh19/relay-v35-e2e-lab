#!/usr/bin/env python3
"""Verify one exact GitHub issue-comment readback against the submitted evidence draft.

The verification is provider GET evidence, not reviewer approval. Never supplies a
GitHub token on CLI; relies on the user's already authenticated `gh` session.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys

REPO = 'reallaksh19/Common'
ISSUE = 875


def verify(comment_id: int, body_path: Path, *, expected_author: str | None = None) -> dict:
    if comment_id <= 0 or not body_path.is_file():
        raise ValueError('positive comment ID and existing body file required')
    endpoint = f'repos/{REPO}/issues/comments/{comment_id}'
    try:
        result = subprocess.run(['gh', 'api', endpoint], check=True, text=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=45)
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        raise ValueError('provider comment GET failed; no readback claim') from exc
    try:
        received = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise ValueError('provider returned invalid JSON') from exc
    expected_url = f'https://github.com/{REPO}/issues/{ISSUE}#issuecomment-{comment_id}'
    expected_issue_api = f'https://api.github.com/repos/{REPO}/issues/{ISSUE}'
    if received.get('html_url') != expected_url or received.get('issue_url') != expected_issue_api:
        raise ValueError('provider URL / target issue mismatch')
    if expected_author and (received.get('user') or {}).get('login') != expected_author:
        raise ValueError('provider author mismatch')
    local = body_path.read_text(encoding='utf-8')
    received_body = (received.get('body') or '').replace('\r\n', '\n')
    if received_body != local.replace('\r\n', '\n'):
        raise ValueError('provider body differs from submitted task evidence file')
    return {
        'schema': 'V35_CAMPAIGN_A_GITHUB_COMMENT_READBACK_V1',
        'source': 'GITHUB_GET_BY_ID',
        'comment_url': expected_url,
        'issue': f'{REPO}#{ISSUE}',
        'author': (received.get('user') or {}).get('login') or 'UNKNOWN',
        'body_sha256': sha256(local.encode('utf-8')).hexdigest(),
        'body_match': True,
        'principal_authenticated_for_reviewer': False,
    }


def main(argv=None) -> int:
    p=argparse.ArgumentParser(description='GET one GitHub task-evidence comment and compare exact submitted text')
    p.add_argument('--comment-id', type=int, required=True)
    p.add_argument('--body-file', type=Path, required=True)
    p.add_argument('--expected-author')
    a=p.parse_args(argv)
    try:
        observed=verify(a.comment_id,a.body_file,expected_author=a.expected_author)
    except (ValueError, OSError, UnicodeError) as exc:
        print(f'GITHUB_READBACK_REJECTED: {exc}',file=sys.stderr)
        return 2
    print(json.dumps(observed,sort_keys=True,indent=2))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
