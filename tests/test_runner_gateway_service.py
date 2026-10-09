"""RNR-06B: actual operator broker process, separate Unix-socket client."""
from __future__ import annotations

import os
import subprocess
import sys
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import runner_gateway as G


class ServiceProcessTests(unittest.TestCase):
    def setUp(self):
        import test_runner_provider
        self.fixture = test_runner_provider.GitBrokerCases('test_real_git_ref_lease_updates_exact_path_and_parent')
        self.fixture.setUp()
        self.folder = self.fixture.root / 'operator-only'
        self.folder.mkdir(mode=0o700)
        self.folder.chmod(0o700)
        self.socket = self.folder / 'lab.sock'
        self.key = self.folder / 'signing.key'
        self.key.write_bytes(b'test-signing-key' * 3)
        self.key.chmod(0o600)
        self.server_path = Path(__file__).resolve().parents[1] / 'scripts/runner_gateway_service.py'
        self.proc = None

    def tearDown(self):
        if self.proc and self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                self.proc.kill()
                self.proc.communicate(timeout=5)
        self.fixture.tearDown()

    def args(self, mode='lab-local'):
        return [sys.executable, str(self.server_path), '--mode', mode,
                '--socket', str(self.socket), '--db', str(self.fixture.db.path),
                '--operator-key-file', str(self.key), '--client-uid', str(os.getuid())]

    def start(self):
        self.proc = subprocess.Popen(
            self.args() + ['--local-remote', str(self.fixture.origin),
                           '--allow-same-uid-in-lab-tests'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            env={'PATH':os.environ.get('PATH', '/usr/bin:/bin')})
        for _ in range(50):
            if self.socket.exists():
                return
            if self.proc.poll() is not None:
                break
            time.sleep(.06)
        self.fail('gateway did not bind private socket: ' + str(self.proc.poll()))

    def test_real_separate_gateway_process_and_socket_commit(self):
        self.start()
        reply = G.send_write_request(self.socket, agent='Agent-A', epoch=1,
                capability=self.fixture.agent_token, operation_id='process-broker-write',
                path='src/inventorylab/parser.py', expected_head=self.fixture.head0,
                content=b'provider commit from separate server process\n')
        self.assertEqual(reply['status'], 'COMMITTED')
        self.assertEqual(self.fixture.provider.head(), reply['new_head'])
        self.assertEqual(self.fixture.db.read('LAB-R1')['active_head'], reply['new_head'])
        self.proc.terminate()
        self.proc.communicate(timeout=5)
        self.assertFalse(self.socket.exists(), 'service should clean socket on SIGTERM')

    def test_gateway_command_does_not_expose_admin_methods(self):
        self.start()
        self.assertEqual(G.send_raw_request(self.socket, b'{"action":"BOOTSTRAP"}\n')['status'],
                         'DENIED')
        self.assertEqual(self.fixture.db.read('LAB-R1')['epoch'], 1)

    def test_local_mode_requires_explicit_test_identity_opt_in(self):
        p = subprocess.run(self.args() + ['--local-remote', str(self.fixture.origin)],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5)
        self.assertEqual(p.returncode, 2)
        self.assertFalse(self.socket.exists())

    def test_github_mode_refuses_lab_same_identity_and_missing_ssh_config(self):
        p = subprocess.run(self.args('github-lab') + ['--allow-same-uid-in-lab-tests'],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5)
        self.assertEqual(p.returncode, 2)
        self.assertFalse(self.socket.exists())

    def test_world_readable_signing_key_fails_closed(self):
        self.key.chmod(0o644)
        p = subprocess.run(self.args() + ['--local-remote', str(self.fixture.origin),
                                          '--allow-same-uid-in-lab-tests'],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5)
        self.assertEqual(p.returncode, 2)
        self.assertFalse(self.socket.exists())


if __name__ == '__main__':
    unittest.main()
