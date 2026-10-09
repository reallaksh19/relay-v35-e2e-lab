#!/usr/bin/env python3
"""RNR-06B private Unix-socket broker deployment *entrypoint*.

Starts no public TCP listener and provides no operator mutation API. A true
GitHub deployment additionally requires separately provisioned service UID,
SSH identity/host trust, exact role permissions and revoked executor tokens.
"""
from __future__ import annotations

import argparse
import os
import signal
import stat
import sys
from pathlib import Path

from runner_custody import CustodyDenied, LabGateway
from runner_gateway import PrivateLabGateway
from runner_provider import BrokeredGitWriter, GitRefProvider


def operator_secret(path: Path) -> bytes:
    if not path.is_absolute() or path.is_symlink():
        raise CustodyDenied("operator key must be an absolute regular non-symlink path")
    info = path.stat()
    if (not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or
            info.st_mode & 0o077):
        raise CustodyDenied("operator signing key ownership or mode unsafe")
    raw = path.read_bytes()
    if len(raw) < 32 or len(raw) > 4096:
        raise CustodyDenied("operator signing secret length invalid")
    return raw


def main() -> int:
    ap = argparse.ArgumentParser(description="RNR-06B lab broker; fail closed by default")
    ap.add_argument('--mode', choices=('lab-local', 'github-lab'), required=True)
    ap.add_argument('--socket', type=Path, required=True)
    ap.add_argument('--db', type=Path, required=True)
    ap.add_argument('--operator-key-file', type=Path, required=True)
    ap.add_argument('--client-uid', type=int, required=True)
    ap.add_argument('--successor-client-uid', type=int,
                    help='separate Agent-B Unix identity; mandatory for GitHub-lab')
    ap.add_argument('--local-remote', type=Path)
    ap.add_argument('--ssh-identity-file', type=Path)
    ap.add_argument('--ssh-known-hosts-file', type=Path)
    ap.add_argument('--allow-same-uid-in-lab-tests', action='store_true')
    args = ap.parse_args()
    try:
        if args.mode == 'lab-local':
            if (args.local_remote is None or not args.local_remote.is_absolute() or
                    args.ssh_identity_file is not None or args.ssh_known_hosts_file is not None):
                raise CustodyDenied("lab-local mode requires only a pinned local absolute remote")
            provider = GitRefProvider(str(args.local_remote), allow_local_test_remote=True)
        else:
            if args.allow_same_uid_in_lab_tests or args.local_remote is not None:
                raise CustodyDenied("real GitHub mode forbids local identity bypass")
            if args.successor_client_uid is None:
                raise CustodyDenied("GitHub-lab requires separate Agent-B Unix identity")
            provider = GitRefProvider(
                'git@github.com:reallaksh19/relay-v35-e2e-lab.git',
                ssh_identity_file=args.ssh_identity_file,
                ssh_known_hosts_file=args.ssh_known_hosts_file,
            )
        if not args.db.is_absolute() or args.db.is_symlink():
            raise CustodyDenied("controller DB path must be absolute and non-symlink")
        secret = operator_secret(args.operator_key_file)
        custody = LabGateway(args.db, secret)
        # Bootstrap and signing keys are never available over the socket.
        server = PrivateLabGateway(
            args.socket, BrokeredGitWriter(custody, provider),
            expected_client_uid=(args.client_uid if args.successor_client_uid is None else None),
            agent_uids=({"Agent-A": args.client_uid,
                         "Agent-B": args.successor_client_uid}
                        if args.successor_client_uid is not None else None),
            allow_same_uid_in_tests=args.allow_same_uid_in_lab_tests,
        )
        # Ensure a service termination closes the socket rather than leaving a
        # potentially stale inode that future operators might wrongly reuse.
        signal.signal(signal.SIGTERM, lambda *_: (_ for _ in ()).throw(KeyboardInterrupt()))
        with server:
            try:
                server.serve_forever(poll_interval=0.1)
            except KeyboardInterrupt:
                pass
        return 0
    except (CustodyDenied, OSError, ValueError) as exc:
        print('RUNNER_GATEWAY_START_DENIED: ' + str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
