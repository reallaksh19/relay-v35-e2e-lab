#!/usr/bin/env python3
"""RNR-06: scoped Git ref CAS writer for a trusted, isolated controller.

Provider-side ref update uses Git push --force-with-lease. This module is NOT
an agent-facing service; it assumes the caller has already authenticated to a
separately hosted broker and has no direct repository write credentials.
"""
from __future__ import annotations

import hashlib
import os
import re
import shlex
import stat
import subprocess
import tempfile
from pathlib import Path
from typing import Callable

from runner_custody import LabGateway, CustodyDenied, ALLOWED_PATHS, require_sha

REF = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]{0,120}$")


class ProviderUncertain(CustodyDenied):
    """Mutation may have reached remote. DO NOT replay automatically."""


class GitRefProvider:
    """Verified branch ref observations + ref-leased Git commit creation.

    `remote` and `branch` MUST be configured by the privileged operator; never
    accept a runner's supplied remote URL. Use a separate private credential
    identity for each hosted broker, never shared with Agent A/B.
    """

    def __init__(self, remote: str, branch: str = "lab/runner-provider-sandbox", *,
                 allow_local_test_remote: bool = False,
                 ssh_identity_file: Path | None = None,
                 ssh_known_hosts_file: Path | None = None):
        if not isinstance(remote, str) or not remote or not isinstance(branch, str) or not REF.fullmatch(branch) or '..' in branch or '//' in branch or branch.endswith(('.lock', '/', '.')):
            raise CustodyDenied("invalid pinned remote or branch")
        if allow_local_test_remote:
            if ssh_identity_file is not None or ssh_known_hosts_file is not None:
                raise CustodyDenied("local test mode cannot accept provider SSH credentials")
            if not Path(remote).resolve().is_dir():
                raise CustodyDenied("local test remote missing")
        elif not re.fullmatch(r"git@github\.com:reallaksh19/relay-v35-e2e-lab\.git", remote):
            raise CustodyDenied("production transport requires pinned lab GitHub repository")
        elif branch != "lab/runner-provider-sandbox":
            raise CustodyDenied("production transport is pinned to disposable sandbox branch")
        self.remote, self.branch = remote, branch
        # Deliberately do not inherit HOME, SSH_AUTH_SOCK, GIT_CONFIG_*,
        # GIT_SSH_COMMAND or repo hooks from an executor process.
        self.env = {'PATH': os.environ.get('PATH', '/usr/bin:/bin'),
                    'GIT_TERMINAL_PROMPT': '0', 'GIT_CONFIG_NOSYSTEM': '1',
                    'GIT_CONFIG_GLOBAL': os.devnull, 'GIT_OPTIONAL_LOCKS': '0'}
        if not allow_local_test_remote:
            def private_file(path: Path | None, mask: int) -> Path:
                if not isinstance(path, Path) or not path.is_absolute() or path.is_symlink():
                    raise CustodyDenied("absolute non-symlink controller SSH file required")
                try:
                    info = path.stat()
                except OSError as exc:
                    raise CustodyDenied("controller SSH configuration unavailable") from exc
                if (not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid()
                        or info.st_mode & mask):
                    raise CustodyDenied("controller SSH file ownership/mode invalid")
                return path
            identity = private_file(ssh_identity_file, 0o077)
            hosts = private_file(ssh_known_hosts_file, 0o022)
            self.env['GIT_SSH_COMMAND'] = (
                'ssh -F /dev/null -o BatchMode=yes -o IdentitiesOnly=yes '
                '-o StrictHostKeyChecking=yes -o GlobalKnownHostsFile=/dev/null '
                '-o UserKnownHostsFile=' + shlex.quote(str(hosts)) +
                ' -i ' + shlex.quote(str(identity))
            )

    def command(self, *args: str, cwd: Path | None = None, input_data: bytes | None = None,
                timeout: int = 15) -> subprocess.CompletedProcess:
        return subprocess.run(['git', *( ['-C', str(cwd)] if cwd else [] ), *args],
                              input=input_data, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, env=self.env, timeout=timeout)

    def head(self) -> str:
        try:
            r = self.command('ls-remote', '--exit-code', self.remote, f'refs/heads/{self.branch}')
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise ProviderUncertain("provider head unavailable") from exc
        lines = r.stdout.decode(errors='replace').splitlines()
        if r.returncode or len(lines) != 1 or '\t' not in lines[0]:
            raise ProviderUncertain("provider exact ref unavailable")
        sha, name = lines[0].split('\t', 1)
        require_sha(sha)
        if name != f'refs/heads/{self.branch}':
            raise ProviderUncertain("provider returned foreign ref")
        return sha

    def commit_and_push(self, old_head: str, path: str, content: bytes, operation_id: str,
                        on_intent: Callable[[str], None]) -> tuple[str, bool]:
        """Create exact candidate, persist intent BEFORE dispatch, then leased push.

        Return (candidate, provider_confirmed). A failed/timeout/ambiguous push
        raises ProviderUncertain so caller must hold the operation for recovery.
        """
        require_sha(old_head)
        if path not in ALLOWED_PATHS or not isinstance(content, bytes) or len(content) > 256000:
            raise CustodyDenied('invalid provider edit')
        with tempfile.TemporaryDirectory(prefix='runner-rnr06-') as tmp:
            root = Path(tmp) / 'objects.git'
            if self.command('init', '--bare', '-q', str(root)).returncode:
                raise CustodyDenied('git init failed')
            fetch = self.command('fetch', '--no-tags', self.remote, f'refs/heads/{self.branch}', cwd=root)
            if fetch.returncode:
                raise ProviderUncertain('fetch not definitive')
            seen = self.command('rev-parse', 'FETCH_HEAD', cwd=root)
            if seen.returncode or seen.stdout.decode().strip() != old_head:
                raise CustodyDenied('candidate changed before mutation')
            env = dict(self.env, GIT_AUTHOR_NAME='Runner Lab Gateway', GIT_AUTHOR_EMAIL='lab-gateway@example.invalid',
                       GIT_COMMITTER_NAME='Runner Lab Gateway', GIT_COMMITTER_EMAIL='lab-gateway@example.invalid',
                       GIT_INDEX_FILE=str(Path(tmp) / 'index'))
            def cmd(*args: str, data: bytes | None = None) -> subprocess.CompletedProcess:
                return subprocess.run(['git', '-C', str(root), *args], input=data,
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, timeout=15)
            if cmd('read-tree', old_head).returncode:
                raise CustodyDenied('cannot read original tree')
            blob = cmd('hash-object', '-w', '--stdin', data=content)
            if blob.returncode:
                raise CustodyDenied('cannot create blob')
            if cmd('update-index', '--add', '--cacheinfo', '100644', blob.stdout.decode().strip(), path).returncode:
                raise CustodyDenied('cannot stage scoped path')
            tree = cmd('write-tree')
            if tree.returncode:
                raise CustodyDenied('cannot construct tree')
            commit = cmd('commit-tree', tree.stdout.decode().strip(), '-p', old_head,
                         data=f'lab(runner): broker write {operation_id}\n'.encode())
            if commit.returncode:
                raise CustodyDenied('cannot construct commit')
            new_head = commit.stdout.decode().strip()
            require_sha(new_head)
            on_intent(new_head)  # durable DB receipt MUST happen before push.
            try:
                push = self.command('push', '--porcelain',
                                    f'--force-with-lease=refs/heads/{self.branch}:{old_head}',
                                    self.remote, f'{new_head}:refs/heads/{self.branch}', cwd=root)
            except (OSError, subprocess.TimeoutExpired) as exc:
                raise ProviderUncertain('push outcome UNKNOWN') from exc
            if push.returncode:
                raise ProviderUncertain('provider CAS push declined/ambiguous')
            if self.head() != new_head:
                raise ProviderUncertain('push response not equal to provider readback')
            return new_head, True


class BrokeredGitWriter:
    """Entry point run INSIDE trusted controller, never given agent credentials."""

    def __init__(self, custody: LabGateway, provider: GitRefProvider):
        self.custody, self.provider = custody, provider

    def write(self, *, agent: str, epoch: int, token: str, operation_id: str,
              path: str, expected_head: str, content: bytes) -> dict:
        if path not in ALLOWED_PATHS or not isinstance(content, bytes) or len(content) > 256000:
            raise CustodyDenied('write scope/size denied before admission')
        # Provider head is a privileged read; broker sees no user-supplied remote.
        self.custody.admit('LAB-R1', agent, epoch, token, operation_id,
                           path, expected_head, self.provider.head)
        try:
            def record(candidate: str) -> None:
                self.custody.record_intent(operation_id, candidate,
                                           hashlib.sha256(content).hexdigest(), self.provider.branch)
            new_head, _ = self.provider.commit_and_push(expected_head, path, content, operation_id, record)
        except ProviderUncertain:
            self.custody.finish(operation_id, 'UNKNOWN', 'PROVIDER_OUTCOME_UNKNOWN', lambda: '')
            raise
        except Exception:
            # If no intent was persisted, no push was dispatched. If an intent
            # exists, even local errors are conservatively held for inspection.
            if self.custody.intent(operation_id) is not None:
                self.custody.finish(operation_id, 'UNKNOWN', 'CANDIDATE_OUTCOME_UNCERTAIN', lambda: '')
            else:
                self.custody.finish(operation_id, 'FAILED', 'PRE_PUSH_CONSTRUCTION_FAILED', self.provider.head)
            raise
        self.custody.finish(operation_id, 'SUCCEEDED', 'GIT_PUSH_AND_HEAD_READBACK', self.provider.head, new_head)
        return {'operation_id': operation_id, 'new_head': new_head,
                'status': 'PROVIDER_CONFIRMED', 'authority': 'LAB_BROKER_ONLY'}
